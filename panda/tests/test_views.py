#!/usr/bin/env python

from django.contrib.auth import authenticate
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
from django.utils.timezone import now

from panda.models import UserProfile, UserProxy
from panda.tests import utils

class TestLogin(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

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

class TestActivate(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        self.user = utils.get_panda_user()
        
        self.client = Client()

    def test_check_activation_key_valid(self):
        new_user = UserProxy.objects.create_user(
            'foo@bar.com',
            'foo@bar.com'
        )
        new_user.is_active = False
        new_user.save()

        user_profile = new_user.get_profile()

        response = self.client.get('/check_activation_key/%s/' % user_profile.activation_key)

        self.assertEqual(response.status_code, 200)
        
        body = json.loads(response.content) 

        self.assertEqual(body['activation_key'], user_profile.activation_key)
        self.assertEqual(body['email'], new_user.email)
        self.assertEqual(body['first_name'], '')
        self.assertEqual(body['last_name'], '')

    def test_check_activation_key_invalid(self):
        response = self.client.get('/check_activation_key/NOT_A_VALID_KEY/')

        self.assertEqual(response.status_code, 400)
        
    def test_activate(self):
        new_user = UserProxy.objects.create_user(
            'foo@bar.com',
            'foo@bar.com'
        )
        new_user.is_active = False
        new_user.save()

        user_profile = new_user.get_profile()
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertGreater(user_profile.activation_key_expiration, now())

        activation_data = {
            'activation_key': user_profile.activation_key,
            'email': 'foo@bar.com',
            'password': 'foobarbaz',
            'reenter_password': 'foobarbaz',
            'first_name': 'Foo',
            'last_name': ''
        }

        response = self.client.post('/activate/', activation_data) 

        self.assertEqual(response.status_code, 200)

        self.assertEqual(authenticate(username='foo@bar.com', password='foobarbaz').pk, new_user.pk)
        
        # Refresh
        user_profile = UserProfile.objects.get(id=user_profile.id)
       
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertLess(user_profile.activation_key_expiration, now())

class  TestForgotPassword(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        self.user = utils.get_panda_user()
        
        self.client = Client()

    def test_forgot_password(self):
        new_user = UserProxy.objects.create_user(
            'foo@bar.com',
            'foo@bar.com',
            'foobarbaz'
        )

        self.assertEqual(authenticate(username='foo@bar.com', password='foobarbaz').pk, new_user.pk)
        
        # Force expiration date into the past
        user_profile = new_user.get_profile() 
        user_profile.activation_key_expiration = now()
        user_profile.save()

        response = self.client.post('/forgot_password/', { 'email': 'foo@bar.com' }) 

        self.assertEqual(response.status_code, 200)

        # Refresh
        user_profile = UserProfile.objects.get(id=user_profile.id)
       
        # Expiration date should be pushed back into the future
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertGreater(user_profile.activation_key_expiration, now())

