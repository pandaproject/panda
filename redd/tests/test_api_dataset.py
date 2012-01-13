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

        self.assertIn('name', errors)

    def test_columns_are_null(self):
        bundle = Bundle(data={ 'columns': None })

        errors = self.validator.is_valid(bundle)

        self.assertNotIn('columns', errors)

    def test_columns_are_array(self):
        bundle = Bundle(data={ 'columns': {} })

        errors = self.validator.is_valid(bundle)

        self.assertIn('columns', errors)

    def test_columns_names_are_strings(self):
        bundle = Bundle(data={ 'columns': [1, 'str'] })

        errors = self.validator.is_valid(bundle)

        self.assertIn('columns', errors)

    def test_columns_are_valid(self):
        bundle = Bundle(data={ 'columns': ['1', 'str'] })

        errors = self.validator.is_valid(bundle)

        self.assertNotIn('columns', errors)

class TestAPIDataset(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

        self.auth_headers = utils.get_auth_headers() 

        self.client = Client()

    def test_get(self):
        # Import so that there will be a task object
        self.dataset.import_data(self.upload, 0)

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
        self.assertEqual(body['columns'], self.dataset.columns)
        self.assertEqual(body['creator']['email'], self.dataset.creator.email)

        task_response = self.client.get('/api/1.0/task/%i/' % self.dataset.current_task.id, **self.auth_headers)

        self.assertEqual(task_response.status_code, 200)

        self.assertEqual(body['current_task'], json.loads(task_response.content))

        self.assertEqual(len(body['related_uploads']), 0)
        self.assertEqual(len(body['data_uploads']), 1)
        self.assertEqual(body['initial_upload'], '/api/1.0/data_upload/%i/' % self.dataset.initial_upload.id)

    def test_get_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug)

        self.assertEqual(response.status_code, 401)

    def test_get_inactive(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 401)

        self.user.is_active = True
        self.user.save()

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
            'description': 'Its got yummy data!'
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'New dataset!')
        self.assertEqual(body['slug'], 'new-dataset')
        self.assertEqual(body['description'], 'Its got yummy data!')
        self.assertEqual(body['row_count'], None)
        self.assertEqual(body['columns'], None)
        self.assertEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['initial_upload'], None)
        self.assertEqual(body['related_uploads'], [])
        self.assertEqual(body['data_uploads'], [])

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertEqual(new_dataset.columns, None)
        self.assertEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.initial_upload, None)
        self.assertEqual(new_dataset.related_uploads.count(), 0)
        self.assertEqual(new_dataset.data_uploads.count(), 0)

    def test_create_post_slug(self):
        # Verify that new slugs are NOT created via POST.
        new_dataset = {
            'slug': 'new-id',
            'name': 'New dataset!',
            'description': 'Its got yummy data!'
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['slug'], 'new-dataset')

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.slug, 'new-dataset')

    def test_create_put(self):
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!'
        }

        response = self.client.put('/api/1.0/dataset/new-id/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'New dataset!')
        self.assertEqual(body['slug'], 'new-id')
        self.assertEqual(body['description'], 'Its got yummy data!')
        self.assertEqual(body['row_count'], None)
        self.assertEqual(body['columns'], None)
        self.assertEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['initial_upload'], None)
        self.assertEqual(body['data_uploads'], [])

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.slug, 'new-id')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertEqual(new_dataset.columns, None)
        self.assertEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.initial_upload, None)
        self.assertEqual(new_dataset.data_uploads.count(), 0)

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
            'description': 'Its got yummy data!'
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **utils.get_auth_headers('tester@tester.com'))

        self.assertEqual(response.status_code, 201)        

    def test_update_readonly(self):
        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug, content_type='application/json', **utils.get_auth_headers('panda@pandaproject.net'))

        data = json.loads(response.content)

        row_count = data['row_count']
        data['row_count'] = 2717

        response = self.client.put('/api/1.0/dataset/%s/' % self.dataset.slug, content_type='application/json', data=json.dumps(data), **utils.get_auth_headers('panda@pandaproject.net'))

        new_data = json.loads(response.content)

        self.assertEqual(new_data['row_count'], row_count)

        # Refresh
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, row_count)

    def test_import_data(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)

        utils.wait() 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertNotEqual(body['current_task'], None)
        self.assertEqual(body['current_task']['task_name'], 'redd.tasks.import.csv')
        
        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 4)
        self.assertEqual(self.dataset.columns, self.upload.columns)
        self.assertEqual(self.dataset.initial_upload, self.upload)
        self.assertEqual(self.dataset.sample_data, self.upload.sample_data)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.task_name, 'redd.tasks.import.csv')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_data_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id))

        self.assertEqual(response.status_code, 401)

    def test_get_datum(self):
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Get id of a datum in Solr
        datum = solr.query(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND Brian' % self.dataset.slug)['response']['docs'][0]

        response = self.client.get('/api/1.0/dataset/%s/data/%s/' % (self.dataset.slug, datum['external_id']), **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(body['external_id'], datum['external_id'])
        self.assertEqual(body['dataset'], '/api/1.0/dataset/%s/' % self.dataset.slug)

    def test_get_data(self):
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            creator=self.dataset.creator)

        # Bending a rules a bit since this upload is associated with the other dataset
        second_dataset.import_data(self.upload, 0)

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['columns'], self.dataset.columns)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 4)
        self.assertEqual(len(body['objects']), 4)
        self.assertEqual(body['objects'][0]['data'][1], 'Brian')

    def test_search_data(self):
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            creator=self.dataset.creator)

        # Bending the rules again...
        second_dataset.import_data(self.upload, 0)

        utils.wait()

        response = self.client.get('/api/1.0/dataset/%s/data/?q=Christopher' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['columns'], self.dataset.columns)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['objects'][0]['data'][1], 'Christopher')

    def test_search_data_limit(self):
        self.dataset.import_data(self.upload, 0)

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
            description='contributors',
            creator=self.dataset.creator)

        # Should match both
        response = self.client.get('/api/1.0/dataset/?q=contributors', **self.auth_headers)

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
        self.assertNotIn('related_uploads', body['objects'][0])
        self.assertNotIn('data_uploads', body['objects'][0])
        self.assertNotIn('sample_data', body['objects'][0])
        self.assertNotIn('current_task', body['objects'][0])

