#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase

from panda.tests import utils

class TestRelatedUpload(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_related_upload(self.user, self.dataset)

    def test_created(self):
        self.assertEqual(self.upload.original_filename, utils.TEST_DATA_FILENAME)
        self.assertEqual(self.upload.creator, self.user)
        self.assertNotEqual(self.upload.creation_date, None)
        self.assertEqual(self.upload.dataset, self.dataset)

