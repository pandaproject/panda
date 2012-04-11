#!/usr/bin/env python

import os

from django.conf import settings
from django.test import TransactionTestCase
from django.test.client import Client

from panda.models import Export
from panda.tests import utils

class TestAPIExport(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        
        utils.setup_test_solr()
        
        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

        self.dataset.import_data(self.user, self.upload, 0)

        self.auth_headers = utils.get_auth_headers()

        self.client = Client()

    def test_download(self):
        self.dataset.export_data(self.user)

        export = Export.objects.get(dataset=self.dataset)

        response = self.client.get('/api/1.0/export/%i/download/' % export.id, **self.auth_headers) 

        self.assertEqual(response.status_code, 200)

        with open(os.path.join(utils.TEST_DATA_PATH, utils.TEST_DATA_FILENAME)) as f:
            self.assertEqual(response.content, f.read())

