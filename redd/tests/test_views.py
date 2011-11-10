#!/usr/bin/env python

from unittest import TestCase

from django.test.client import Client
from django.utils import simplejson as json

from redd.tests import utils

class TestLogin(TestCase):
    def setUp(self):
        self.user = utils.get_test_user()
        
        self.client = Client()

    def test_login_success(self):
        response = self.client.post('/login/', { 'username': 'panda', 'password': 'panda' }) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['username'], 'panda')
        self.assertEqual(body['api_key'], 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b')

    def test_login_disabled(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post('/login/', { 'username': 'panda', 'password': 'panda' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('disabled', body['__all__'])

        self.user.is_active = True
        self.user.save()

    def test_login_invalid_username(self):
        response = self.client.post('/login/', { 'username': 'NOTPANDA', 'password': 'panda' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('incorrect', body['__all__'])

    def test_login_incorrect_password(self):
        response = self.client.post('/login/', { 'username': 'panda', 'password': 'NOTPANDA' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertIn('incorrect', body['__all__'])

    def test_no_get(self):
        response = self.client.get('/login/', { 'username': 'panda', 'password': 'NOTPANDA' }) 

        self.assertEqual(response.status_code, 400)

        body = json.loads(response.content)

        self.assertEqual(body, None)

