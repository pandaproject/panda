#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest

from redd.api.data import DataResource, DataValidation
from redd.models import Dataset
from redd.tests import utils

class TestDataValidation(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        self.validator = DataValidation()

        self.user = utils.get_panda_user()
        self.upload = utils.get_test_upload(self.user)
        self.dataset = utils.get_test_dataset(self.upload, self.user)

    def test_required_fields(self):
        bundle = Bundle(data={})

        errors = self.validator.is_valid(bundle, None)

        self.assertIn('data', errors)
        self.assertIn('required', errors['data'][0])


class TestAPIData(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
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

        # Returned as a list of datasets
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(int(body['objects'][0]['id']), self.dataset.id)
        self.assertEqual(body['objects'][0]['meta']['total_count'], 4)
        self.assertEqual(len(body['objects'][0]['objects']), 4)

        datum = body['objects'][0]['objects'][0]

        response = self.client.get('/api/1.0/data/%s/' % datum['id'], **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        get_result = json.loads(response.content)

        self.assertEqual(datum, get_result)

    def test_get_404(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/not-a-valid-id/', **self.auth_headers)
        self.assertEqual(response.status_code, 404)

    def test_list(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Returned as a list of datasets
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(int(body['objects'][0]['id']), self.dataset.id)
        self.assertEqual(body['objects'][0]['meta']['total_count'], 4)
        self.assertEqual(len(body['objects'][0]['objects']), 4)

        self.assertIn('data', body['objects'][0]['objects'][0])
        self.assertIn('id', body['objects'][0]['objects'][0])
        self.assertIn('resource_uri', body['objects'][0]['objects'][0])
        self.assertIn('row', body['objects'][0]['objects'][0])

    def test_list_unauthorized(self):
        response = self.client.get('/api/1.0/data/')

        self.assertEqual(response.status_code, 401)   

    def test_get_dataset_from_bundle_request_or_kwargs_bundle(self):
        data_resource = DataResource()

        bundle = Bundle(data={ 'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug })
        
        dataset = data_resource.get_dataset_from_bundle_request_or_kwargs(bundle, None)

        self.assertEqual(dataset.id, self.dataset.id)

    def test_get_dataset_from_bundle_request_or_kwargs_kwargs(self):
        data_resource = DataResource()

        bundle = Bundle(data={})
        
        dataset = data_resource.get_dataset_from_bundle_request_or_kwargs(bundle, dataset_slug=self.dataset.slug)

        self.assertEqual(dataset.id, self.dataset.id)

    def test_get_dataset_from_bundle_request_or_kwargs_agree(self):
        data_resource = DataResource()

        bundle = Bundle(data={ 'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug })
        
        dataset = data_resource.get_dataset_from_bundle_request_or_kwargs(bundle, dataset_slug=self.dataset.slug)

        self.assertEqual(dataset.id, self.dataset.id)

    def test_get_dataset_from_bundle_request_or_kwargs_conflict(self):
        data_resource = DataResource()

        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        bundle = Bundle(data={ 'dataset': '/api/1.0/dataset/%s/' % second_dataset.slug })
        
        with self.assertRaises(BadRequest):
            data_resource.get_dataset_from_bundle_request_or_kwargs(bundle, dataset_slug=self.dataset.slug)

    def test_get_dataset_from_bundle_request_or_kwargs_none(self):
        data_resource = DataResource()

        bundle = Bundle(data={})
        
        with self.assertRaises(BadRequest):
            data_resource.get_dataset_from_bundle_request_or_kwargs(bundle)

    def test_create_no_dataset(self):
        new_data = {
            'data': ['1', '2', '3']
        }

        response = self.client.post('/api/1.0/data/', content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 400)

    def test_create_data_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        new_data = {
            'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
            'data': ['1', '2', '3']
        }

        response = self.client.post('/api/1.0/data/', content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 201)
        body = json.loads(response.content)
        self.assertEqual(body['data'], new_data['data'])
        self.assertEqual(body['dataset'], new_data['dataset'])
        self.assertIn('id', body)
        self.assertIn('dataset', body)
        self.assertIn('resource_uri', body)
        self.assertIn('row', body)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 5)

    def test_create_data_endpoint_bulk(self):
        self.dataset.import_data()

        utils.wait()

        new_data = { 'objects': [
            {
                'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
                'data': ['1', '2', '3']
            },
            {
                'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
                'data': ['4', '5', '6']
            }
        ]}

        response = self.client.put('/api/1.0/data/', content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 202)
        body = json.loads(response.content)
        self.assertEqual(len(body['objects']), 2)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 6)

    def test_create_dataset_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        new_data = {
            'data': ['1', '2', '3']
        }

        response = self.client.post('/api/1.0/dataset/%s/data/' % self.dataset.slug, content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 201)
        body = json.loads(response.content)
        self.assertEqual(body['data'], new_data['data'])
        self.assertIn('id', body)
        self.assertIn('dataset', body)
        self.assertIn('resource_uri', body)
        self.assertIn('row', body)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 5)

    def test_create_dataset_endpoint_bulk(self):
        self.dataset.import_data()

        utils.wait()

        new_data = { 'objects': [
            {
                'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
                'data': ['1', '2', '3']
            },
            {
                'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
                'data': ['4', '5', '6']
            }
        ]}

        response = self.client.put('/api/1.0/dataset/%s/data/' % self.dataset.slug, content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 202)
        body = json.loads(response.content)
        self.assertEqual(len(body['objects']), 2)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 6)

    def test_created_search(self):
        self.dataset.import_data()

        utils.wait()

        new_data = {
            'data': ['Flibbity!', '2', '3']
        }

        response = self.client.post('/api/1.0/dataset/%s/data/' % self.dataset.slug, content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/1.0/data/?q=flibbity', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Verify that the group count is correct
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)

    def test_create_too_few_fields(self):
        new_data = {
            'data': ['Mr.', 'PANDA']
        }

        response = self.client.post('/api/1.0/dataset/%s/data/' % self.dataset.slug, content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('data', body)

    def test_create_too_many_fields(self):
        new_data = {
            'data': ['Mr.', 'PANDA', 'PANDA Project', 'PANDAs everywhere']
        }

        response = self.client.post('/api/1.0/dataset/%s/data/' % self.dataset.slug, content_type='application/json', data=json.dumps(new_data), **self.auth_headers)

        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('data', body)

    def test_update_data_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        update_data = {
            'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
            'data': ['1', '2', '3']
        }

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        # Dataset objects were returned
        data = body['objects'][0]['objects'][0]

        response = self.client.put('/api/1.0/data/%s/' % data['id'], content_type='application/json', data=json.dumps(update_data), **self.auth_headers)

        self.assertEqual(response.status_code, 202)
        body = json.loads(response.content)
        self.assertEqual(body['data'], update_data['data'])
        self.assertEqual(body['dataset'], data['dataset'])
        self.assertEqual(body['resource_uri'], data['resource_uri'])
        self.assertEqual(body['row'], None)

    def test_update_dataset_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        update_data = {
            'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
            'data': ['1', '2', '3']
        }

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        # Dataset objects were returned
        data = body['objects'][0]['objects'][0]

        response = self.client.put('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, data['id']), content_type='application/json', data=json.dumps(update_data), **self.auth_headers)

        self.assertEqual(response.status_code, 202)
        body = json.loads(response.content)
        self.assertEqual(body['data'], update_data['data'])
        self.assertEqual(body['dataset'], data['dataset'])
        self.assertEqual(body['resource_uri'], data['resource_uri'])
        self.assertEqual(body['row'], None)

    def test_updated_search(self):
        self.dataset.import_data()

        utils.wait()

        update_data = {
            'dataset': '/api/1.0/dataset/%s/' % self.dataset.slug,
            'data': ['Flibbity!', '2', '3']
        }

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        # Dataset objects were returned
        data = body['objects'][0]['objects'][0]

        response = self.client.put('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, data['id']), content_type='application/json', data=json.dumps(update_data), **self.auth_headers)

        self.assertEqual(response.status_code, 202)

        response = self.client.get('/api/1.0/data/?q=flibbity', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Verify that the group count is correct
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)

    def test_delete_data_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        # Dataset objects were returned
        data = body['objects'][0]['objects'][0]

        response = self.client.delete('/api/1.0/data/%s/' % data['id'], content_type='application/json', **self.auth_headers)

        self.assertEqual(response.status_code, 204)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 3)

    def test_delete_dataset_endpoint(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        data = body['objects'][0]

        response = self.client.delete('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, data['id']), content_type='application/json', **self.auth_headers)

        self.assertEqual(response.status_code, 204)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 3)

    def test_deleted_search(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/', **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)

        # Dataset objects were returned
        data = body['objects'][0]['objects'][0]

        response = self.client.delete('/api/1.0/data/%s/' % data['id'], content_type='application/json', **self.auth_headers)

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/1.0/data/?q=%s' % data['data'][0], **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Verify that the group count is correct
        self.assertEqual(body['meta']['total_count'], 0)
        self.assertEqual(len(body['objects']), 0)

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

        response = self.client.get('/api/1.0/data/?q=Christopher', **self.auth_headers)

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

    def test_search_meta(self):
        self.dataset.import_data()

        utils.wait()

        # Import second dataset so we can make sure both match 
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        second_dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/data/?q=Ryan&limit=1', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        # Verify that the group count is correct
        self.assertEqual(body['meta']['limit'], 1)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['total_count'], 2)
        self.assertIs(body['meta']['previous'], None)
        self.assertIsNot(body['meta']['next'], None)
        self.assertEqual(len(body['objects']), 1)

    def test_search_boolean_query(self):
        self.dataset.import_data()

        utils.wait()
        
        response = self.client.get('/api/1.0/data/?q=Brian+and+Tribune', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)

    def test_search_unauthorized(self):
        response = self.client.get('/api/1.0/data/?q=Christopher')

        self.assertEqual(response.status_code, 401)   

