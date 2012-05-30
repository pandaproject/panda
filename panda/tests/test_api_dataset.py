#!/usr/bin/env python

from time import sleep

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json
from django.utils.timezone import now
from tastypie.bundle import Bundle

from panda import solr
from panda.api.datasets import DatasetValidation
from panda.models import Category, Dataset
from panda.tests import utils

class TestDatasetValidation(TestCase):
    def setUp(self):
        self.validator = DatasetValidation()

    def test_required_fields(self):
        bundle = Bundle(data={})

        errors = self.validator.is_valid(bundle)

        self.assertIn('name', errors)

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
        self.dataset.import_data(self.user, self.upload, 0)

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        response = self.client.get('/api/1.0/dataset/%s/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['description'], self.dataset.description)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['sample_data'], self.dataset.sample_data)
        self.assertEqual(body['column_schema'], self.dataset.column_schema)
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
        self.dataset.update_full_text()

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
        self.assertEqual(body['column_schema'], None)
        self.assertEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['initial_upload'], None)
        self.assertEqual(body['related_uploads'], [])
        self.assertEqual(body['data_uploads'], [])

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertEqual(new_dataset.column_schema, None)
        self.assertEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.initial_upload, None)
        self.assertEqual(new_dataset.related_uploads.count(), 0)
        self.assertEqual(new_dataset.data_uploads.count(), 0)

    def test_create_post_slug(self):
        # Verify that new slugs are NOT created via POST.
        new_dataset = {
            'slug': 'new-slug',
            'name': 'New dataset!',
            'description': 'Its got yummy data!'
        }

        response = self.client.post('/api/1.0/dataset/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual(body['slug'], 'new-slug')

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.slug, 'new-slug')

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
        self.assertEqual(body['column_schema'], None)
        self.assertEqual(body['sample_data'], None)
        self.assertEqual(body['current_task'], None)
        self.assertEqual(body['initial_upload'], None)
        self.assertEqual(body['data_uploads'], [])

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.name, 'New dataset!')
        self.assertEqual(new_dataset.slug, 'new-id')
        self.assertEqual(new_dataset.description, 'Its got yummy data!')
        self.assertEqual(new_dataset.row_count, None)
        self.assertEqual(new_dataset.column_schema, None)
        self.assertEqual(new_dataset.sample_data, None)
        self.assertEqual(new_dataset.current_task, None)
        self.assertEqual(new_dataset.initial_upload, None)
        self.assertEqual(new_dataset.data_uploads.count(), 0)

    def test_create_put_twice(self):
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!'
        }

        response = self.client.put('/api/1.0/dataset/new-slug/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        update_dataset = {
            'name': 'Updated dataset!'
        }
        
        body = json.loads(response.content)

        self.assertEqual(body['name'], 'New dataset!')
        self.assertEqual(body['slug'], 'new-slug')
        dataset_id = body['id']

        response = self.client.put('/api/1.0/dataset/new-slug/', content_type='application/json', data=json.dumps(update_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 202)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'Updated dataset!')
        self.assertEqual(body['slug'], 'new-slug')
        self.assertEqual(body['id'], dataset_id)

        # One dataset is created by setup
        self.assertEqual(Dataset.objects.all().count(), 2)

    def test_put_different_slug(self):
        new_dataset = {
            'name': 'New dataset!',
            'description': 'Its got yummy data!'
        }

        response = self.client.put('/api/1.0/dataset/new-slug/', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        update_dataset = {
            'slug': 'changed-slug',
            'name': 'Updated dataset!'
        }

        response = self.client.put('/api/1.0/dataset/new-slug/', content_type='application/json', data=json.dumps(update_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 202)

        body = json.loads(response.content)

        self.assertEqual(body['slug'], 'new-slug')
        
        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual(new_dataset.slug, 'new-slug')

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

    def test_create_with_schema(self):
        new_dataset = {
            'name': 'New dataset!'
        }

        response = self.client.post('/api/1.0/dataset/?columns=foo,bar,baz&typed_columns=True,,False&column_types=int,unicode,date', content_type='application/json', data=json.dumps(new_dataset), **self.auth_headers)

        self.assertEqual(response.status_code, 201)

        body = json.loads(response.content)

        self.assertEqual([c['name'] for c in body['column_schema']], ['foo', 'bar', 'baz'])
        self.assertEqual([c['indexed'] for c in body['column_schema']], [True, False, False])
        self.assertEqual([c['type'] for c in body['column_schema']], ['int', 'unicode', 'date'])

        new_dataset = Dataset.objects.get(id=body['id'])

        self.assertEqual([c['name'] for c in new_dataset.column_schema], ['foo', 'bar', 'baz'])
        self.assertEqual([c['indexed'] for c in new_dataset.column_schema], [True, False, False])
        self.assertEqual([c['type'] for c in new_dataset.column_schema], ['int', 'unicode', 'date'])

    def test_import_data(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertNotEqual(body['current_task'], None)
        self.assertEqual(body['current_task']['task_name'], 'panda.tasks.import.csv')
        
        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 4)
        self.assertEqual([c['name'] for c in self.dataset.column_schema], self.upload.columns)
        self.assertEqual(self.dataset.initial_upload, self.upload)
        self.assertEqual(self.dataset.sample_data, self.upload.sample_data)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.task_name, 'panda.tasks.import.csv')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_data_locked(self):
        # Note - testing a race condition here, should find a better way
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)

        self.assertEqual(response.status_code, 403)

    def test_import_data_unauthorized(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id))

        self.assertEqual(response.status_code, 401)

    def test_reindex_data(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)

        response = self.client.get('/api/1.0/dataset/%s/reindex/?typed_columns=True,False,False,False' % (self.dataset.slug), **self.auth_headers)

        self.assertEqual(response.status_code, 200)
        
        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertEqual(self.dataset.row_count, 4)
        self.assertEqual([c['name'] for c in self.dataset.column_schema], self.upload.columns)
        self.assertEqual(self.dataset.initial_upload, self.upload)
        self.assertEqual(self.dataset.sample_data, self.upload.sample_data)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.task_name, 'panda.tasks.reindex')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:3')['response']['numFound'], 1)

    def test_reindex_data_no_data(self):
        response = self.client.get('/api/1.0/dataset/%s/reindex/' % (self.dataset.slug), **self.auth_headers)

        self.assertEqual(response.status_code, 400)

    def test_reindex_data_invalid_columns(self):
        response = self.client.get('/api/1.0/dataset/%s/import/%i/' % (self.dataset.slug, self.upload.id), **self.auth_headers)

        response = self.client.get('/api/1.0/dataset/%s/reindex/?typed_columns=True,False,False' % (self.dataset.slug), **self.auth_headers)

        self.assertEqual(response.status_code, 400)

    def test_export_data(self):
        self.dataset.import_data(self.user, self.upload, 0)

        response = self.client.get('/api/1.0/dataset/%s/export/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertNotEqual(body['current_task'], None)
        self.assertEqual(body['current_task']['task_name'], 'panda.tasks.export.csv')
        
        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.task_name, 'panda.tasks.export.csv')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

    def test_get_datum(self):
        self.dataset.import_data(self.user, self.upload, 0)

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
        self.dataset.import_data(self.user, self.upload, 0)

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            creator=self.dataset.creator)

        # Bending a rules a bit since this upload is associated with the other dataset
        second_dataset.import_data(self.user, self.upload, 0)

        response = self.client.get('/api/1.0/dataset/%s/data/' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['column_schema'], self.dataset.column_schema)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 4)
        self.assertEqual(len(body['objects']), 4)
        self.assertEqual(body['objects'][0]['data'][1], 'Brian')

    def test_search_data(self):
        self.dataset.import_data(self.user, self.upload, 0)

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            creator=self.dataset.creator)

        # Bending the rules again...
        second_dataset.import_data(self.user, self.upload, 0)

        response = self.client.get('/api/1.0/dataset/%s/data/?q=Christopher' % self.dataset.slug, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['column_schema'], self.dataset.column_schema)

        # Test that only one dataset was matched
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['objects'][0]['data'][1], 'Christopher')

    def test_search_data_limit(self):
        self.dataset.import_data(self.user, self.upload, 0)

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

    def test_search_data_since(self):
        self.dataset.import_data(self.user, self.upload, 0)

        # Refetch dataset so that attributes will be updated
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        # Import second dataset so we can make sure only one is matched
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            creator=self.dataset.creator)

        second_dataset.import_data(self.user, self.upload, 0)

        between_time = now().replace(microsecond=0, tzinfo=None)
        between_time = between_time.isoformat('T')
        sleep(1)

        # Import 2nd dataset again, to verify only one is matched
        second_dataset.import_data(self.user, self.upload, 0)

        response = self.client.get('/api/1.0/dataset/%s/data/?q=Christopher&since=%s' % (self.dataset.slug, between_time), **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)
        
        # Verify that correct attributes of the dataset are attached
        self.assertEqual(int(body['id']), self.dataset.id)
        self.assertEqual(body['name'], self.dataset.name)
        self.assertEqual(body['row_count'], self.dataset.row_count)
        self.assertEqual(body['column_schema'], self.dataset.column_schema)

        # Test that only one dataset and one import was matched
        self.assertEqual(body['meta']['total_count'], 1)
        self.assertEqual(len(body['objects']), 1)

    def test_search_datasets(self):
        second_dataset = Dataset.objects.create(
            name='Second dataset',
            description='contributors',
            creator=self.dataset.creator)
        second_dataset.update_full_text()

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

    def test_delete(self):
        dataset_id = self.dataset.id
        response = self.client.delete('/api/1.0/dataset/%s/' % (self.dataset.slug), **self.auth_headers)

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/1.0/dataset/%s/' % (self.dataset.slug), **self.auth_headers)

        self.assertEqual(response.status_code, 404)

        with self.assertRaises(Dataset.DoesNotExist):
            Dataset.objects.get(id=dataset_id)

    def test_creator_email_filter(self):
        response = self.client.get('/api/1.0/dataset/', data={ 'creator_email': self.user.email }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 1)
        self.assertEqual(body['meta']['total_count'], 1)

        response = self.client.get('/api/1.0/dataset/', data={ 'creator_email': utils.get_admin_user().email }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), 0)
        self.assertEqual(body['meta']['total_count'], 0)

