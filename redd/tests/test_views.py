#!/usr/bin/env python

from unittest import TestCase

from django.contrib.auth.models import User
from django.test.client import Client
from django.utils import simplejson as json

from redd.tests import utils

class TestLogin(TestCase):
    def setUp(self):
        self.user = utils.get_panda_user()
        
        self.client = Client()

    def test_login_success(self):
        response = self.client.post('/login/', { 'email': 'user@pandaproject.net', 'password': 'user' }) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['email'], 'user@pandaproject.net')
        self.assertEqual(body['api_key'], 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84c')
        self.assertEqual(body['notifications'], [])

    def test_login_disabled(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post('/login/', { 'email': 'user@pandaproject.net', 'password': 'user' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('disabled', body['__all__'])

        self.user.is_active = True
        self.user.save()

    def test_login_invalid_email(self):
        response = self.client.post('/login/', { 'email': 'NOTPANDA@pandaproject.net', 'password': 'panda' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('incorrect', body['__all__'])

    def test_login_incorrect_password(self):
        response = self.client.post('/login/', { 'email': 'user@pandaproject.net', 'password': 'NOPANDA' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('incorrect', body['__all__'])

    def test_no_get(self):
        response = self.client.get('/login/', { 'email': 'user@pandaproject.net', 'password': 'NOPANDA' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertEqual(body, None)

class TestRegistration(TestCase):
    def setUp(self):
        self.user = utils.get_panda_user()
        
        self.client = Client()

    def test_registration_success(self):
        response = self.client.post('/register/', { 'email': 'NEWPANDA@pandaproject.net', 'password': 'panda', 'first_name': 'Mr.', 'last_name': 'PANDA' }) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['email'], 'newpanda@pandaproject.net')
        self.assertIn('api_key', body)
        self.assertEqual(body['notifications'], [])

        new_user = User.objects.get(username='newpanda@pandaproject.net')

        self.assertEqual(new_user.username, 'newpanda@pandaproject.net')
        self.assertEqual(new_user.email, 'newpanda@pandaproject.net')
        self.assertEqual(new_user.first_name, 'Mr.')
        self.assertEqual(new_user.last_name, 'PANDA')

    def test_registration_email_already_in_use(self):
        response = self.client.post('/register/', { 'email': 'user@pandaproject.net', 'password': 'NEWPANDA' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('already registered', body['__all__'])

    def test_validation(self):
        response = self.client.post('/register/', { 'email': 'INVALID' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('email', body)

