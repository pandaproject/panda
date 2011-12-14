#!/usr/bin/env python

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test import TransactionTestCase
from django.utils import simplejson as json

from redd import solr
from redd.models import Dataset, TaskStatus
from redd.tests import utils

class TestDataset(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.upload = utils.get_test_upload(self.user)
        self.dataset = utils.get_test_dataset(self.upload, self.user)

    def test_schema_created(self):
        self.assertNotEqual(self.dataset.schema, None)
        self.assertEqual(len(self.dataset.schema), 4)
        self.assertEqual(self.dataset.schema[0], {
            'column': 'id',
            'type': 'int'
        });

    def test_sample_data_created(self):
        self.assertNotEqual(self.dataset.sample_data, None)
        self.assertEqual(len(self.dataset.sample_data), 4)
        self.assertEqual(self.dataset.sample_data[0], ['1', 'Brian', 'Boyer', 'Chicago Tribune']);

    def test_metadata_searchable(self):
        response = solr.query(settings.SOLR_DATASETS_CORE, 'contributors', sort='slug asc')

        self.assertEqual(response['response']['numFound'], 1)

    def test_import_data(self):
        self.dataset.import_data(0)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.DatasetImportTask')

        utils.wait()

        # Refresh from database
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_delete(self):
        self.dataset.import_data(0)

        utils.wait()

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

        dataset_id = self.dataset.id
        self.dataset.delete()

        utils.wait()

        with self.assertRaises(Dataset.DoesNotExist):
            Dataset.objects.get(id=dataset_id)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 0)

        response = solr.query(settings.SOLR_DATASETS_CORE, 'contributors', sort='slug asc')

        self.assertEqual(response['response']['numFound'], 0)

    def test_get_row(self):
        self.dataset.import_data(0)

        utils.wait()

        row = self.dataset.get_row('1')

        self.assertEqual(row['external_id'], '1')
        self.assertEqual(json.loads(row['data']), ['1', 'Brian', 'Boyer', 'Chicago Tribune'])

    def test_get_row_not_found(self):
        self.dataset.import_data(0)

        utils.wait()

        row = self.dataset.get_row('5')

        self.assertEqual(row, None)

    def test_add_row(self):
        self.dataset.import_data(0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        new_row =['5', 'Somebody', 'Else', 'Somewhere']

        self.dataset.add_row(new_row, external_id='5')
        row = self.dataset.get_row('5')

        self.assertEqual(row['external_id'], '5')
        self.assertEqual(json.loads(row['data']), new_row)
        self.assertEqual(self.dataset.row_count, 5)
        self.assertEqual(self.dataset.modified, True)
        self.assertEqual(self.dataset._count_rows(), 5)

    def test_add_row_already_exists(self):
        self.dataset.import_data(0)

        utils.wait()

        new_row =['1', 'Somebody', 'Else', 'Somewhere']

        with self.assertRaises(ObjectDoesNotExist):
            self.dataset.add_row(new_row, external_id='1')

    def test_update_row(self):
        self.dataset.import_data(0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        update_row =['1', 'Somebody', 'Else', 'Somewhere']

        self.dataset.update_row('1', update_row)
        row = self.dataset.get_row('1')

        self.assertEqual(row['external_id'], '1')
        self.assertEqual(json.loads(row['data']), update_row)
        self.assertEqual(self.dataset.row_count, 4)
        self.assertEqual(self.dataset.modified, True)
        self.assertEqual(self.dataset._count_rows(), 4)

    def test_update_row_not_found(self):
        self.dataset.import_data(0)

        utils.wait()

        update_row =['5', 'Somebody', 'Else', 'Somewhere']

        with self.assertRaises(ObjectDoesNotExist):
            self.dataset.update_row('5', update_row)

    def test_update_row_old_data_deleted(self):
        self.dataset.import_data(0)

        utils.wait()

        update_row =['1', 'Somebody', 'Else', 'Somewhere']

        self.dataset.update_row('1', update_row)

        self.assertEqual(self.dataset._count_rows(), 4)

    def test_delete_row(self):
        self.dataset.import_data(0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.delete_row('1')
        row = self.dataset.get_row('1')

        self.assertEqual(row, None)
        self.assertEqual(self.dataset.row_count, 3)
        self.assertEqual(self.dataset.modified, True)
        self.assertEqual(self.dataset._count_rows(), 3)

    def test_delete_row_not_found(self):
        self.dataset.import_data(0)

        utils.wait()

        with self.assertRaises(ObjectDoesNotExist):
            self.dataset.delete_row('5')

