#!/usr/bin/env python

import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from panda.models import DataUpload
from panda.tests import utils

class TestPurgeOrphanedUploads(TestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)
        self.related = utils.get_test_related_upload(self.user, self.dataset)

    def test_delete_orphaned_file(self):
        orphan_filepath = os.path.join(settings.MEDIA_ROOT, 'IM_AN_ORPHANED_FILE.csv')
        open(orphan_filepath, 'w').close()

        call_command('purge_orphaned_uploads')

        self.assertEqual(os.path.exists(orphan_filepath), False)

    def test_dont_delete_data_file(self):
        call_command('purge_orphaned_uploads')

        self.assertEqual(os.path.exists(self.upload.get_path()), True)

    def test_dont_delete_related_file(self):
        call_command('purge_orphaned_uploads')

        self.assertEqual(os.path.exists(self.related.get_path()), True)

    def test_delete_orphaned_data_upload(self):
        self.upload.dataset = None
        self.upload.save()

        call_command('purge_orphaned_uploads')

        with self.assertRaises(DataUpload.DoesNotExist):
            DataUpload.objects.get(id=self.upload.id)

        self.assertEqual(os.path.exists(self.upload.get_path()), False)

