#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client
from django.utils import simplejson as json

from panda.models import Category 
from panda.tests import utils

class TestAPICategories(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        
        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

        self.auth_headers = utils.get_auth_headers()

        self.client = Client()

    def test_get(self):
        category = Category.objects.get(slug='crime')

        # No datasets in category
        response = self.client.get('/api/1.0/category/%s/' % category.slug, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['name'], 'Crime')
        self.assertEqual(body['slug'], 'crime')
        self.assertEqual(body['dataset_count'], 0)

        # One dataset in category
        category.datasets.add(self.dataset)

        response = self.client.get('/api/1.0/category/%s/' % category.slug, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(body['dataset_count'], 1)


    def test_list(self):
        categories = Category.objects.all()

        # Dataset not in category
        response = self.client.get('/api/1.0/category/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        self.assertEqual(len(body['objects']), len(categories) + 1)
        self.assertEqual(body['meta']['total_count'], len(categories))
        self.assertEqual(body['meta']['limit'], 5)
        self.assertEqual(body['meta']['offset'], 0)
        self.assertEqual(body['meta']['next'], None)
        self.assertEqual(body['meta']['previous'], None)
        
        uncategorized = next(c for c in body['objects'] if c['slug'] == 'uncategorized')

        self.assertEqual(uncategorized['dataset_count'], 1)

        # Dataset in category
        categories[0].datasets.add(self.dataset)

        response = self.client.get('/api/1.0/category/', data={ 'limit': 5 }, **self.auth_headers)

        self.assertEqual(response.status_code, 200)

        body = json.loads(response.content)

        uncategorized = next(c for c in body['objects'] if c['slug'] == 'uncategorized')

        self.assertEqual(uncategorized['dataset_count'], 0)
        
