#!/usr/bin/env python

from django.contrib.auth import authenticate
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json

from panda.models import User
from panda.tests import utils

class TestLogin(TransactionTestCase):
    fixtures = ['init_panda.json']

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

class  TestActivate(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        self.user = utils.get_panda_user()
        
        self.client = Client()

    def test_check_activation_key_valid(self):
        new_user = User.objects.create(
            email="foo@bar.com",
            username="foo@bar.com",
            is_active=False
        )

        key = new_user.get_profile().activation_key

        response = self.client.get('/check_activation_key/%s/' % key)

        self.assertEqual(response.status_code, 200)
        
        body = json.loads(response.content) 

        self.assertEqual(body['activation_key'], key)
        self.assertEqual(body['email'], new_user.email)
        self.assertEqual(body['first_name'], '')
        self.assertEqual(body['last_name'], '')

    def test_check_activation_key_invalid(self):
        response = self.client.get('/check_activation_key/NOT_A_VALID_KEY/')

        self.assertEqual(response.status_code, 400)
        
    def test_activate(self):
        new_user = User.objects.create(
            email="foo@bar.com",
            username="foo@bar.com",
            is_active=False
        )

        response = self.client.post('/activate/', { 'activation_key': new_user.get_profile().activation_key, 'email': 'foo@bar.com', 'password': 'foobarbaz' }) 

        self.assertEqual(response.status_code, 200)

        self.assertEqual(authenticate(username='foo@bar.com', password='foobarbaz'), new_user)
        
