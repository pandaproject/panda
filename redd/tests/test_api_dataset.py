#!/usr/bin/env python

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
from tastypie.bundle import Bundle

from redd import solr
from redd.api.datasets import DatasetValidation
from redd.models import Category, Dataset
from redd.tests import utils

class TestDatasetValidation(TestCase):
    def setUp(self):
        self.validator = DatasetValidation()

    def test_required_fields(self):
        bundle = Bundle(data={})

        errors = self.validator.is_valid(bundle)

        self.assertIn("name", errors)

class TestAPIDataset(TransactionTestCase):
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
        # Import so that there will be a task object
        self.dataset.import_data()

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['description'], self.dataset.description)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['sample_data'], self.dataset.sample_data)
        self.assertEqual(body['schema'], self.dataset.schema)
        self.assertEqual(body['creator']['email'], self.dataset.creator.email)

        task_response = self.client.get('/api/1.0/task/%i/' % self.dataset.current_task.id, **self.auth_headers)

        self.assertEqual(task_response.status_code, 200)

        self.assertEqual(body['current_task'], json.loads(task_response.content))

        upload_response = self.client.get('/api/1.0/upload/%i/' % self.dataset.data_upload.id, **self.auth_headers)

        self.assertEqual(upload_response.status_code, 200)

        self.assertEqual(body['data_upload'], json.loads(upload_response.content))

    def test_get_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug)

        self.assertEqual(response.status_code, 401)

    def test_list(self):
        response = self.client.get('/api/1.0/dataset/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)

    def test_list_filtered_by_category_miss(self):
        response = self.client.get('/api/1.0/dataset/', data={ 'category': 'crime' }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 0)
        self.assertEqual(body['meta']['total_count'], 0)

    def test_list_filtered_by_category_hit(self):
        category = Category.objects.get(slug='crime')
        self.dataset.categories.add(category)
        self.dataset.save()

        response = self.client.get('/api/1.0/dataset/', data={ 'category': 'crime' }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(int(body['objects'][0]['id']), self.dataset.id)

    def test_create_post(self):
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!',
            'data_upload': '/api/1.0/upload/%i/' % self.upload.id
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'New dataset!')
        self.assertEqual(body['slug'], 'new-dataset')
        self.assertEqual(body['description'], 'Its got yummy data!')
        self.assertEqual(body['row_count'], None)
        self.assertNotEqual(body['schema'], None)
        self.assertNotEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['data_upload']['filename'], self.upload.filename)
        self.assertEqual(body['creator']['email'], self.user.email)

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertNotEqual(new_dataset.schema, None)
        self.assertNotEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.data_upload, self.upload)
        self.assertEqual(new_dataset.creator, self.user)

    def test_create_post_no_data_upload(self):
        new_dataset = {
            'name': 'This dataset does not have an upload!'
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'This dataset does not have an upload!')
        self.assertEqual(body['row_count'], None)
        self.assertEqual(body['schema'], None)
        self.assertEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['data_upload'], None)

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'This dataset does not have an upload!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertEqual(new_dataset.schema, None)
        self.assertEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.data_upload, None)

    def test_create_put(self):
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!',
            'data_upload': '/api/1.0/upload/%i/' % self.upload.id
        }

        response = self.client.put('/api/1.0/dataset/new-id/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'New dataset!')
        # TODO: This is wrong.
        self.assertEqual(body['slug'], 'new-id')
        self.assertEqual(body['description'], 'Its got yummy data!')
        self.assertEqual(body['row_count'], None)
        self.assertNotEqual(body['schema'], None)
        self.assertNotEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['data_upload']['filename'], self.upload.filename)
        self.assertEqual(body['creator']['email'], self.user.email)

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.slug, 'new-id')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertNotEqual(new_dataset.schema, None)
        self.assertNotEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.data_upload, self.upload)
        self.assertEqual(new_dataset.creator, self.user)

    def test_create_as_new_user(self):
        new_user = {
            'email': 'tester@tester.com',
            'password': 'test',
            'first_name': 'Testy',
            'last_name': 'McTester'
        }

        response = self.client.post('/api/1.0/user/', content_type='application/json', data=json.dumps(new_user), **utils.get_auth_headers('panda@pandaproject.net'))

        self.assertEqual(response.status_code, 201)
        
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!',
            'data_upload': '/api/1.0/upload/%i/' % self.upload.id
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **utils.get_auth_headers('tester@tester.com'))

        self.assertEqual(response.status_code, 201)        

    def test_import_data(self):
        response = self.client.get('/api/1.0/dataset/%s/import/' % self.dataset.slug, **self.auth_headers)

        utils.wait() 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertNotEqual(body['current_task'], None)
        self.assertEqual(body['current_task']['task_name'], 'redd.tasks.DatasetImportTask')
        
        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 4)
        self.assertNotEqual(self.dataset.schema, None)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.task_name, 'redd.tasks.DatasetImportTask')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_data_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/import/' % self.dataset.slug)

        self.assertEqual(response.status_code, 401)

    def test_get_datum(self):
        self.dataset.import_data()

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Get id of a datum in Solr
        datum = solr.query(settings.SOLR_DATA_CORE, 'dataset_id:%s Brian' % self.dataset.id)['response']['docs'][0]

        response = self.client.get('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, datum['id']), **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(body['id'], datum['id'])
        self.assertEqual(body['row'], 1)
        self.assertEqual(body['dataset'], '/api/1.0/dataset/%s/' % self.dataset.slug)

    def test_get_datum_from_wrong_dataset(self):
        self.dataset.import_data()

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        second_dataset.import_data()

        utils.wait()

        # Get id of a datum in Solr
        datum = solr.query(settings.SOLR_DATA_CORE, 'dataset_id:%s Brian' % second_dataset.id)['response']['docs'][0]

        response = self.client.get('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, datum['id']), **self.auth_headers)

        self.assertEqual(response.status_code, 404)

    def test_get_data(self):
        self.dataset.import_data()

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        second_dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['schema'], self.dataset.schema)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 4)
        self.assertEqual(len(body['objects']), 4)
        self.assertEqual(body['objects'][0]['data'][0], 'Brian')

    def test_search_data(self):
        self.dataset.import_data()

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        second_dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/?q=Christopher' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['schema'], self.dataset.schema)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['objects'][0]['data'][0], 'Christopher')

    def test_search_data_limit(self):
        self.dataset.import_data()

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/?q=Tribune&limit=1' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['limit'], 1)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['total_count'], 2)
        self.assertIs(body['meta']['previous'], None)
        self.assertIsNot(body['meta']['next'], None)
        self.assertEqual(len(body['objects']), 1)

    def test_search_data_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/data/?q=Christopher' % self.dataset.slug)

        self.assertEqual(response.status_code, 401)

    def test_search_datasets(self):
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            data_upload=self.dataset.data_upload,
            creator=self.dataset.creator)

        # Should match both
        response = self.client.get('/api/1.0/dataset/?q=contributors.csv', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total_count'], 2)
        self.assertEqual(len(body['objects']), 2)

        # Should match only the second dataset
        response = self.client.get('/api/1.0/dataset/?q=second', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(int(body['objects'][0]['id']), second_dataset.id)

    def test_search_datasets_simple(self):
        response = self.client.get('/api/1.0/dataset/?q=contributors&simple=true', **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(int(body['objects'][0]['id']), self.dataset.id)
        self.assertNotIn('data_upload', body['objects'][0])
        self.assertNotIn('sample_data', body['objects'][0])
        self.assertNotIn('current_task', body['objects'][0])
        self.assertNotIn('dialect', body['objects'][0])

