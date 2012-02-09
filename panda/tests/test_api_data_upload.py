#!/usr/bin/env python

import os.path

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json

from panda.models import DataUpload
from panda.tests import utils

class TestAPIDataUpload(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

        self.auth_headers = utils.get_auth_headers()

        self.client = Client()

    def test_get(self):
        response = self.client.get('/api/1.0/data_upload/%i/' % self.upload.id, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['filename'], self.upload.filename)
        self.assertEqual(body['original_filename'], self.upload.original_filename)
        self.assertEqual(body['size'], self.upload.size)
        self.assertEqual(body['creator']['resource_uri'], '/api/1.0/user/%i/' % self.user.id)
        self.assertNotEqual(body['creation_date'], None)
        self.assertEqual(body['dataset'], '/api/1.0/dataset/%s/' % self.dataset.slug)
        self.assertEqual(body['data_type'], 'csv')
        self.assertEqual(body['columns'], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(len(body['sample_data']), 4)
        self.assertEqual(body['sample_data'][0], ['1', 'Brian', 'Boyer', 'Chicago Tribune'])

    def test_get_unauthorized(self):
        response = self.client.get('/api/1.0/data_upload/%i/' % self.upload.id)

        self.assertEqual(response.status_code, 401)

    def test_list(self):
        response = self.client.get('/api/1.0/data_upload/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_create_denied(self):
        new_upload = {
            'filename': 'test.csv',
            'original_filename': 'test.csv',
            'size': 20
        }

        response = self.client.post('/api/1.0/data_upload/', content_type='application/json', data=json.dumps(new_upload), **self.auth_headers)

        self.assertEqual(response.status_code, 405)

    def test_download(self):
        response = self.client.get('/api/1.0/data_upload/%i/download/' % self.upload.id, **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=%s' % self.upload.original_filename)
        self.assertEqual(int(response['Content-Length']), self.upload.size)

        with open(os.path.join(settings.MEDIA_ROOT, utils.TEST_DATA_FILENAME)) as f:
            self.assertEqual(f.read(), response.content)

    def test_download_unauthorized(self):
        response = self.client.get('/api/1.0/data_upload/%i/download/' % self.upload.id)

        self.assertEqual(response.status_code, 401)

    def test_upload_file(self):
        with open(os.path.join(settings.MEDIA_ROOT, utils.TEST_DATA_FILENAME)) as f:
            response = self.client.post('/data_upload/', data={ 'file': f, 'dataset_slug': self.dataset.slug }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        self.assertEqual(body['success'], True)

        upload = DataUpload.objects.get(id=body['id'])

        self.assertEqual(body['original_filename'], upload.original_filename)
        self.assertEqual(body['size'], os.path.getsize(os.path.join(settings.MEDIA_ROOT, utils.TEST_DATA_FILENAME)))
        self.assertEqual(body['size'], upload.size)
        self.assertEqual(body['creator']['resource_uri'], '/api/1.0/user/%i/' % self.user.id)

    def test_upload_unauthorized(self):
        with open(os.path.join(settings.MEDIA_ROOT, utils.TEST_DATA_FILENAME)) as f:
            response = self.client.post('/data_upload/', data={ 'file': f })

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        self.assertEqual(body['success'], False)
        self.assertEqual(body['forbidden'], True)

    def test_delete(self):
        response = self.client.delete('/api/1.0/data_upload/%i/' % self.upload.id, **self.auth_headers)

        self.assertEqual(response.status_code, 204)

