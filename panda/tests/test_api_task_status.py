#!/usr/bin/env python

from datetime import datetime

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
import pytz

from panda.models import TaskStatus
from panda.tests import utils

class TestAPITaskStatus(TransactionTestCase):
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
        task = TaskStatus.objects.get(id=self.dataset.current_task.id)

        response = self.client.get('/api/1.0/task/%i/' % task.id, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['status'], task.status)
        self.assertEqual(body['task_name'], task.task_name)
        start = datetime.strptime(body['start'], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.timezone('Etc/UTC'))
        self.assertEqual(start, task.start.replace(microsecond=0))
        end = datetime.strptime(body['end'], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.timezone('Etc/UTC'))
        self.assertEqual(end, task.end.replace(microsecond=0))
        self.assertEqual(body['message'], task.message)
        self.assertEqual(body['traceback'], None)
        self.assertNotEqual(body['creator'], None)

    def test_get_unauthorized(self):
        response = self.client.get('/api/1.0/task/%i/' % self.dataset.current_task.id) 

        self.assertEqual(response.status_code, 401)

    def test_list(self):
        response = self.client.get('/api/1.0/task/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_create_denied(self):
        new_task = {
            'task_name': 'panda.tasks.ImportDatasetTask'
        }

        response = self.client.post('/api/1.0/task/', content_type='application/json', data=json.dumps(new_task), **self.auth_headers)

        self.assertEqual(response.status_code, 405)

