#!/usr/bin/env python

import os.path

from django.conf import settings
from django.test import TransactionTestCase
from django.utils import simplejson as json

from redd import solr
from redd.models import Dataset, DataUpload, TaskStatus
from redd.tests import utils

class TestDataset(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_metadata_searchable(self):
        response = solr.query(settings.SOLR_DATASETS_CORE, 'contributors', sort='slug asc')

        self.assertEqual(response['response']['numFound'], 1)

    def test_import_csv(self):
        self.dataset.import_data(self.upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.import.csv')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_xls(self):
        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)

        self.dataset.import_data(xls_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.import.xls')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xls_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_excel_xlsx(self):
        xlsx_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_EXCEL_XLSX_FILENAME)

        self.dataset.import_data(xlsx_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.import.xlsx')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xlsx_upload = DataUpload.objects.get(id=xlsx_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xlsx_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_oo_xlsx(self):
        xlsx_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_OO_XLSX_FILENAME)

        self.dataset.import_data(xlsx_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.import.xlsx')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xlsx_upload = DataUpload.objects.get(id=xlsx_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xlsx_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_additional_data_same_columns(self):
        self.dataset.import_data(self.upload)

        utils.wait()

        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.import_data(xls_upload)

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        
        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 8)
        self.assertEqual(upload.imported, True)
        self.assertEqual(xls_upload.imported, True)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 2)
    
    def test_import_additional_data_different_columns(self):
        self.dataset.import_data(self.upload)

        utils.wait()

        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)
        xls_upload.columns = ['id', 'first_name', 'last_name', 'employer', 'MORE COLUMNS!']
        xls_upload.save()
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertRaises(TypeError, self.dataset.import_data, xls_upload)

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        
        self.assertEqual(dataset.columns, ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(upload.imported, True)
        self.assertEqual(xls_upload.imported, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_delete(self):
        self.dataset.import_data(self.upload)

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
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        row = self.dataset.get_row('1')

        self.assertEqual(row['external_id'], '1')
        self.assertEqual(json.loads(row['data']), ['1', 'Brian', 'Boyer', 'Chicago Tribune'])

    def test_add_row(self):
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        new_row =['5', 'Somebody', 'Else', 'Somewhere']

        self.dataset.add_row(self.user, new_row, external_id='5')
        row = self.dataset.get_row('5')

        self.assertEqual(row['external_id'], '5')
        self.assertEqual(json.loads(row['data']), new_row)
        self.assertEqual(self.dataset.row_count, 5)
        self.assertNotEqual(self.dataset.last_modified, None)
        self.assertEqual(self.dataset._count_rows(), 5)

    def test_delete_row(self):
        self.dataset.import_data(self.upload, 0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.delete_row(self.user, '1')
        row = self.dataset.get_row('1')

        self.assertEqual(row, None)
        self.assertEqual(self.dataset.row_count, 3)
        self.assertNotEqual(self.dataset.last_modified, None)
        self.assertEqual(self.dataset._count_rows(), 3)

    def test_export_csv(self):
        self.dataset.import_data(self.upload)

        utils.wait()

        self.dataset.export_data('test_export.csv')

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'redd.tasks.export.csv')

        utils.wait()

        # Refresh from database
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        with open(os.path.join(utils.TEST_DATA_PATH, utils.TEST_DATA_FILENAME), 'r') as f:
            imported_csv = f.read()

        with open(os.path.join(settings.MEDIA_ROOT, 'test_export.csv')) as f:
            exported_csv = f.read()

        self.assertEqual(imported_csv, exported_csv)

