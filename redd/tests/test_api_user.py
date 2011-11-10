#!/usr/bin/env python

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json
from tastypie.bundle import Bundle

from redd.api.users import UserValidation
from redd.tests import utils

class TestUserValidation(TestCase):
    def setUp(self):
        self.validator = UserValidation()

    def test_required_fields(self):
        bundle = Bundle(data={})

        errors = self.validator.is_valid(bundle)

        self.assertIn("username", errors)
        self.assertIn("email", errors)

    def test_invalid_usernames(self):
        for username in ['jim123!', '#lucky', 'space boy', 'SELECT * FROM', '']:
            bundle = Bundle(data={ 'username': username })
        
            errors = self.validator.is_valid(bundle)

            print username
            self.assertIn("username", errors)

    def test_valid_usernames(self):
        for username in ['jim123', 'lucky', 'space_boy', 'SELECT-ALL-FROM']:
            bundle = Bundle(data={ 'username': username })
        
            errors = self.validator.is_valid(bundle)

            self.assertNotIn("username", errors)

    def test_invalid_emails(self):
        for email in ['nobody.com', 'nobody@', 'nobody@nobody', 'nobody@.com', '']:
            bundle = Bundle(data={ 'email': email })
        
            errors = self.validator.is_valid(bundle)

            self.assertIn("email", errors)

    def test_valid_emails(self):
        for email in ['nobody@nobody.com', 'nobody.nobody@somewhere.com', 'no_body@no-body.re']:
            bundle = Bundle(data={ 'email': email })
        
            errors = self.validator.is_valid(bundle)

            self.assertNotIn("email", errors)

    def test_password_missing(self):
        bundle = Bundle(data={ 'username': 'panda', 'email': 'panda@pandaproject.net' })

        self.validator.is_valid(bundle)

        self.assertEqual(bundle.data['password'], None)

    def test_password_supplied(self):
        bundle = Bundle(data={ 'username': 'panda', 'email': 'panda@pandaproject.net', 'password': 'panda' })

        self.validator.is_valid(bundle)

        self.assertEqual(bundle.data['password'][:5], 'sha1$')

class TestAPIUser(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_test_user() 
        
        self.auth_headers = utils.get_auth_headers()

        self.client = Client()

    def test_get(self):
        response = self.client.get('/api/1.0/user/%i/' % self.user.id, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertNotIn('password', body)

    def test_get_unauthorized(self):
        response = self.client.get('/api/1.0/user/%i/' % self.user.id) 

        self.assertEqual(response.status_code, 401)

    def test_list(self):
        response = self.client.get('/api/1.0/user/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_create_denied(self):
        new_user = {
            'username': 'tester',
            'password': 'INVALID'
        }

        response = self.client.post('/api/1.0/user/', content_type='application/json', data=json.dumps(new_user), **self.auth_headers)

        self.assertEqual(response.status_code, 405)

