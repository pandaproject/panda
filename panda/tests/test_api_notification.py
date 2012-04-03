#!/usr/bin/env python

from datetime import datetime

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
import pytz

from panda.models import Notification, User 
from panda.tests import utils

class TestAPINotifications(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        
        utils.setup_test_solr()
        
        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

        self.dataset.import_data(self.user, self.upload, 0)

        utils.wait()

        self.auth_headers = utils.get_auth_headers()

        self.client = Client()

    def test_get(self):
        notification = Notification.objects.get(related_dataset=self.dataset)

        response = self.client.get('/api/1.0/notification/%i/' % notification.id, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        sent_at = datetime.strptime(body['sent_at'], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.timezone('Etc/UTC'))
        self.assertEqual(sent_at, notification.sent_at.replace(microsecond=0))
        self.assertEqual(body['read_at'], None)
        self.assertEqual(body['message'], notification.message)

    def test_get_not_recipient(self):
        response = self.client.get('/api/1.0/notification/%i/' % self.dataset.current_task.id) 

        self.assertEqual(response.status_code, 401)

    def test_get_unauthorized(self):
        User.objects.create_user('nobody@nobody.com', 'nobody@nobody.com', 'password')

        notification = Notification.objects.get(related_dataset=self.dataset)

        response = self.client.get('/api/1.0/notification/%i/' % notification.id, **utils.get_auth_headers('nobody@nobody.com')) 

        self.assertEqual(response.status_code, 404)

    def test_list(self):
        response = self.client.get('/api/1.0/notification/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_list_unauthorized(self):
        User.objects.create_user('nobody@nobody.com', 'nobody@nobody.com', 'password')

        response = self.client.get('/api/1.0/notification/?', data={ 'limit': 5 }, **utils.get_auth_headers('nobody@nobody.com')) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 0)
        self.assertEqual(body['meta']['total_count'], 0)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_update(self):
        notification = Notification.objects.get(related_dataset=self.dataset)

        data = json.dumps({ 'read_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') })

        response = self.client.put('/api/1.0/notification/%i/' % notification.id, data=data, content_type='application/json', **self.auth_headers) 

        self.assertEqual(response.status_code, 204)

        # Refresh
        notification = Notification.objects.get(related_dataset=self.dataset)

        self.assertNotEqual(notification.read_at, None)

    def test_update_unauthorized(self):
        User.objects.create_user('nobody@nobody.com', 'nobody@nobody.com', 'password')

        notification = Notification.objects.get(related_dataset=self.dataset)

        data = json.dumps({ 'read_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') })

        response = self.client.put('/api/1.0/notification/%i/' % notification.id, data=data, content_type='application/json', **utils.get_auth_headers('nobody@nobody.com')) 
        # This returns 201 (rather than 401), because the PUT fails to match an
        # existing notification that the user has access to and thus falls
        # back to creating a new one.
        # This is probably not ideal, but works.
        self.assertEqual(response.status_code, 201)

