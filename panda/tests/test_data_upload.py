#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase

from panda.tests import utils

class TestDataUpload(TransactionTestCase):
    fixtures = ['init_panda.json']

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

