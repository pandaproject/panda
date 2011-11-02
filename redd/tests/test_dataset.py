#!/usr/bin/env python

from time import sleep

from django.conf import settings
from django.test import TestCase

from redd.models import Dataset, TaskStatus
from redd.tests import utils

class TestDataset(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.solr = utils.get_test_solr() 

        self.upload = utils.get_test_upload()
        self.dataset = utils.get_test_dataset(self.upload)

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

        sleep(utils.SLEEP_DELAY)

        # Refresh from database
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 1)

    def test_delete(self):
        self.dataset.import_data()

        sleep(utils.SLEEP_DELAY)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 1)

        dataset_id = self.dataset.id
        self.dataset.delete()

        sleep(utils.SLEEP_DELAY)

        with self.assertRaises(Dataset.DoesNotExist):
            Dataset.objects.get(id=dataset_id)

        self.assertEqual(self.solr.query('Christopher').execute().result.numFound, 0)

