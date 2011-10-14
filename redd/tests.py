#!/usr/bin/env python

from django.test.client import Client
from django.test import TestCase

from redd.models import Dataset

class TestAPI(TestCase):
    def setUp(self):
        self.upload = Upload.objects.create(
            filename='test',
            original_filename='original_test',
            size='1')

        self.dataset = Dataset.objects.create(
            name='test',
            description='description',
            data_upload=self.upload)

        self.client = Client()

    def test_dataset_get(self):
        self.assertEqual(1 + 1, 2)
