#!/usr/bin/env python

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json

from redd.tests import utils

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

