#!/usr/bin/env python

import os.path
from shutil import copyfile
from time import sleep

from django.conf import settings
from django.test import TestCase
from sunburnt import SolrInterface

from redd.models import Dataset, TaskStatus, Upload

TEST_DATA_PATH = os.path.join(settings.SITE_ROOT, 'test_data')
TEST_DATA_FILENAME = 'contributors.csv'

SLEEP_DELAY = 3

class TestDataset(TestCase):
    def setUp(self):
        settings.SOLR_ENDPOINT = 'http://localhost:8983/solr/data_test'
        settings.CELERY_ALWAYS_EAGER = True

        self.solr = SolrInterface(settings.SOLR_ENDPOINT) 
        self.solr.delete(queries='*:*', commit=True)

        # Ensure panda subdir has been created
        try:
            os.mkdir(settings.MEDIA_ROOT)
        except OSError:
            pass

        src = os.path.join(TEST_DATA_PATH, TEST_DATA_FILENAME)
        dst = os.path.join(settings.MEDIA_ROOT, TEST_DATA_FILENAME)
        copyfile(src, dst)

        self.upload = Upload.objects.create(
            filename=TEST_DATA_FILENAME,
            original_filename=TEST_DATA_FILENAME,
            size=os.path.getsize(dst))

        self.dataset = Dataset.objects.create(
            name='Contributors',
            description='Biographic information about contributors to the PANDA project.',
            data_upload=self.upload)

    def test_schema_created(self):
        self.assertNotEqual(self.dataset.schema, None)
        self.assertEqual(len(self.dataset.schema), 3)
        self.assertEqual(self.dataset.schema[0], {
            'column': 'first_name',
            'simple_type': 'unicode',
            'meta_type': None,
            'indexed': False
        });

    def test_sample_data_created(self):
        self.assertNotEqual(self.dataset.sample_data, None)
        self.assertEqual(len(self.dataset.sample_data), 4)
        self.assertEqual(self.dataset.sample_data[0], {
            'row': 1,
            'data': ['Brian', 'Boyer', 'Chicago Tribune']
        });

    def test_import_data(self):
        self.dataset.import_data()

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.DatasetImportTask')

        sleep(SLEEP_DELAY)

        # Refresh from database
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 1)

    def test_delete(self):
        self.dataset.import_data()

        sleep(SLEEP_DELAY)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 1)

        dataset_id = self.dataset.id
        self.dataset.delete()

        sleep(SLEEP_DELAY)

        with self.assertRaises(Dataset.DoesNotExist):
            Dataset.objects.get(id=dataset_id)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 0)

