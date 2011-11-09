#!/usr/bin/env python

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json

from redd.models import Dataset
from redd.tests import utils

class TestAPIData(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.solr = utils.get_test_solr() 

        self.user = utils.get_test_user()
        self.upload = utils.get_test_upload(self.user)
        self.dataset = utils.get_test_dataset(self.upload, self.user)

        self.auth_headers = utils.get_auth_headers()

        self.client = Client()
    
    def test_get(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/', **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        list_result = body['objects'][0]

        response = self.client.get('/api/1.0/data/%s/' % list_result['id'], **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        get_result = json.loads(response.content)

        self.assertEqual(list_result, get_result)

    def test_list(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total_count'], 4)
        self.assertEqual(body['objects'][0]['dataset'], '/api/1.0/dataset/%i/' % self.dataset.id)
        self.assertIn('data', body['objects'][0])
        self.assertIn('id', body['objects'][0])
        self.assertIn('resource_uri', body['objects'][0])
        self.assertIn('row', body['objects'][0])

    def test_list_unauthorized(self):
        response = self.client.get('/api/1.0/data/')

        self.assertEqual(response.status_code, 401)   

    def test_create_denied(self):
        new_data = {
            'dataset': '/api/1.0/dataset/%i/' % self.dataset.id,
            'data': ['1', '2', '3']
        }

        response = self.client.post('/api/1.0/data/', content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 405)

    def test_search(self):
        self.dataset.import_data()

        utils.wait()

        # Import second dataset so we can make sure both match 
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        second_dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/search/?q=Christopher', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Verify that the group count is correct
        self.assertEqual(body['meta']['total_count'], 2)
        self.assertEqual(len(body['objects']), 2)

        # Verify that each matched dataset includes one result
        for result_dataset in body['objects']:
            self.assertEqual(result_dataset['meta']['total_count'], 1)
            self.assertEqual(len(result_dataset['objects']), 1)

            db_dataset = Dataset.objects.get(id=result_dataset['id'])
            
            self.assertEqual(result_dataset['name'], db_dataset.name)
            self.assertEqual(result_dataset['row_count'], db_dataset.row_count)
            self.assertEqual(result_dataset['schema'], db_dataset.schema)

            self.assertEqual(result_dataset['objects'][0]['data'][0], 'Christopher')
            self.assertIn('id', result_dataset['objects'][0])
            self.assertIn('resource_uri', result_dataset['objects'][0])
            self.assertIn('row', result_dataset['objects'][0])

    def test_search_unauthorized(self):
        response = self.client.get('/api/1.0/data/search/?q=Christopher')

        self.assertEqual(response.status_code, 401)   

