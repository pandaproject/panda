#!/usr/bin/env python

import os.path

from django.conf import settings
from django.test import TransactionTestCase

from panda import solr
from panda.models import Dataset, DataUpload
from panda.tests import utils

class TestDataUpload(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_created(self):
        upload = utils.get_test_data_upload(self.user, self.dataset)

        self.assertEqual(upload.original_filename, utils.TEST_DATA_FILENAME)
        self.assertEqual(upload.creator, self.user)
        self.assertNotEqual(upload.creation_date, None)
        self.assertEqual(upload.dataset, self.dataset)

        self.assertEqual(upload.data_type, 'csv')
        self.assertNotEqual(self.upload.dialect, None)
        self.assertEqual(self.upload.columns, ['id', 'first_name', 'last_name', 'employer']);
        self.assertEqual(len(self.upload.sample_data), 4)
        self.assertEqual(self.upload.sample_data[0], ['1', 'Brian', 'Boyer', 'Chicago Tribune']);
        
        self.assertEqual(len(self.upload.guessed_types), 4)
        self.assertEqual(self.upload.guessed_types, ['int', 'unicode', 'unicode', 'unicode']);

    def test_delete(self):
        upload = utils.get_test_data_upload(self.user, self.dataset)
        upload_id = upload.id
        path = upload.get_path()

        self.assertEqual(os.path.isfile(path), True)

        solr.delete(settings.SOLR_DATA_CORE, '*:*')
        self.dataset.import_data(self.user, upload)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)
        
        dataset = Dataset.objects.get(id=self.dataset.id)
        self.assertEqual(dataset.initial_upload, upload)

        upload.delete()

        # Ensure dataset still exists
        dataset = Dataset.objects.get(id=self.dataset.id)
        self.assertEqual(dataset.initial_upload, None)

        self.assertEqual(os.path.exists(path), False)

        with self.assertRaises(DataUpload.DoesNotExist):
            DataUpload.objects.get(id=upload_id)
        
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 0)

