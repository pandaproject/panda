#!/usr/bin/env python

import os.path

from django.conf import settings
from django.test import TransactionTestCase
from django.utils import simplejson as json

from panda import solr
from panda.exceptions import DatasetLockedError, DataImportError
from panda.models import Dataset, DataUpload, TaskStatus
from panda.tests import utils
from panda.utils.column_schema import update_indexed_names

class TestDataset(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_lock(self):
        self.dataset.lock()
        self.assertEqual(self.dataset.locked, True)

    def test_lock_fail(self):
        self.dataset.lock()
        self.assertRaises(DatasetLockedError, self.dataset.lock)

    def test_unlock(self):
        self.dataset.lock()
        self.dataset.unlock()
        self.dataset.lock()
        self.dataset.unlock()

        self.assertEqual(self.dataset.locked, False)

    def test_metadata_searchable(self):
        response = solr.query(settings.SOLR_DATASETS_CORE, 'contributors', sort='slug asc')

        self.assertEqual(response['response']['numFound'], 1)

    def test_import_csv(self):
        self.dataset.import_data(self.user, self.upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'panda.tasks.import.csv')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], [None, None, None, None])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_xls(self):
        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)

        self.dataset.import_data(self.user, xls_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'panda.tasks.import.xls')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], [None, None, None, None])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xls_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_excel_xlsx(self):
        xlsx_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_EXCEL_XLSX_FILENAME)

        self.dataset.import_data(self.user, xlsx_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'panda.tasks.import.xlsx')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xlsx_upload = DataUpload.objects.get(id=xlsx_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xlsx_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_oo_xlsx(self):
        xlsx_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_OO_XLSX_FILENAME)

        self.dataset.import_data(self.user, xlsx_upload)

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'panda.tasks.import.xlsx')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        xlsx_upload = DataUpload.objects.get(id=xlsx_upload.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], [None, None, None, None])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(xlsx_upload.imported, True)
        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_additional_data_same_columns(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.import_data(self.user, xls_upload)

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        
        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], [None, None, None, None])
        self.assertEqual(dataset.row_count, 8)
        self.assertEqual(upload.imported, True)
        self.assertEqual(xls_upload.imported, True)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 2)
    
    def test_import_additional_data_different_columns(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        xls_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)
        xls_upload.columns = ['id', 'first_name', 'last_name', 'employer', 'MORE COLUMNS!']
        xls_upload.save()
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.assertRaises(DataImportError, self.dataset.import_data, self.user, xls_upload)

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        upload = DataUpload.objects.get(id=self.upload.id)
        xls_upload = DataUpload.objects.get(id=xls_upload.id)
        
        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(upload.imported, True)
        self.assertEqual(xls_upload.imported, False)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 1)

    def test_import_additional_csv_typed_columns(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        second_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_DATA_FILENAME)
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.import_data(self.user, second_upload)

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        
        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed'] for c in dataset.column_schema], [True, False, True, True])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], ['column_int_id', None, 'column_unicode_last_name', 'column_unicode_employer'])
        self.assertEqual(dataset.row_count, 8)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:2')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_last_name:Germuska')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_first_name:Joseph')['response']['numFound'], 0)

    def test_import_additional_xls_typed_columns(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        second_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_XLS_FILENAME)
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.import_data(self.user, second_upload)

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        
        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed'] for c in dataset.column_schema], [True, False, True, True])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], ['column_int_id', None, 'column_unicode_last_name', 'column_unicode_employer'])
        self.assertEqual(dataset.row_count, 8)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:2')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_last_name:Germuska')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_first_name:Joseph')['response']['numFound'], 0)

    def test_import_additional_xlsx_typed_columns(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        second_upload = utils.get_test_data_upload(self.user, self.dataset, utils.TEST_EXCEL_XLSX_FILENAME)
        
        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        self.dataset.import_data(self.user, second_upload)

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        
        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed'] for c in dataset.column_schema], [True, False, True, True])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], ['column_int_id', None, 'column_unicode_last_name', 'column_unicode_employer'])
        self.assertEqual(dataset.row_count, 8)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'Christopher')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:2')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_last_name:Germuska')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_first_name:Joseph')['response']['numFound'], 0)

    def test_delete(self):
        self.dataset.import_data(self.user, self.upload)

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
        self.dataset.import_data(self.user, self.upload, 0)

        utils.wait()

        row = self.dataset.get_row('1')

        self.assertEqual(row['external_id'], '1')
        self.assertEqual(json.loads(row['data']), ['1', 'Brian', 'Boyer', 'Chicago Tribune'])

    def test_add_row(self):
        self.dataset.import_data(self.user, self.upload, 0)

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

    def test_add_many_rows(self):
        self.dataset.import_data(self.user, self.upload, 0)

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        new_rows = [
            (['5', 'Somebody', 'Else', 'Somewhere'], 5),
            (['6', 'Another', 'Person', 'Somewhere'], 6)
        ]

        self.dataset.add_many_rows(self.user, new_rows)
        row = self.dataset.get_row('6')

        self.assertEqual(row['external_id'], '6')
        self.assertEqual(json.loads(row['data']), new_rows[1][0])
        self.assertEqual(self.dataset.row_count, 6)
        self.assertNotEqual(self.dataset.last_modified, None)
        self.assertEqual(self.dataset._count_rows(), 6)

    def test_add_row_typed(self):
        self.dataset.import_data(self.user, self.upload, 0)

        utils.wait()

        self.dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        # Refresh from database
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        new_row =['5', 'Somebody', 'Else', 'Somewhere']

        self.dataset.add_row(self.user, new_row, external_id='5')
        row = self.dataset.get_row('5')

        self.assertEqual(row['external_id'], '5')
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:5')['response']['numFound'], 1)

    def test_add_many_rows_typed(self):
        self.dataset.import_data(self.user, self.upload, 0)

        utils.wait()

        self.dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        # Refresh dataset so row_count is available
        self.dataset = Dataset.objects.get(id=self.dataset.id)

        new_rows = [
            (['5', 'Somebody', 'Else', 'Somewhere'], 5),
            (['6', 'Another', 'Person', 'Somewhere'], 6)
        ]

        self.dataset.add_many_rows(self.user, new_rows)
        row = self.dataset.get_row('6')

        self.assertEqual(row['external_id'], '6')
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:[5 TO 6]')['response']['numFound'], 2)

    def test_delete_row(self):
        self.dataset.import_data(self.user, self.upload, 0)

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
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        self.dataset.export_data(self.user, 'test_export.csv')

        task = self.dataset.current_task

        self.assertNotEqual(task, None)
        self.assertNotEqual(task.id, None)
        self.assertEqual(task.task_name, 'panda.tasks.export.csv')

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)
        self.assertEqual(dataset.locked, False)

        with open(os.path.join(utils.TEST_DATA_PATH, utils.TEST_DATA_FILENAME), 'r') as f:
            imported_csv = f.read()

        with open(os.path.join(settings.EXPORT_ROOT, 'test_export.csv')) as f:
            exported_csv = f.read()

        self.assertEqual(imported_csv, exported_csv)

    def test_reindex(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)

        dataset.reindex_data(self.user, typed_columns=[True, False, True, True])

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        task = dataset.current_task

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['id', 'first_name', 'last_name', 'employer'])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['int', 'unicode', 'unicode', 'unicode'])
        self.assertEqual([c['indexed'] for c in dataset.column_schema], [True, False, True, True])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], ['column_int_id', None, 'column_unicode_last_name', 'column_unicode_employer'])
        self.assertEqual([c['min'] for c in dataset.column_schema], [1, None, None, None])
        self.assertEqual([c['max'] for c in dataset.column_schema], [4, None, None, None])
        self.assertEqual(dataset.row_count, 4)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_int_id:2')['response']['numFound'], 1)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_last_name:Germuska')['response']['numFound'], 1)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_first_name:Joseph')['response']['numFound'], 0)

    def test_reindex_complex(self):
        upload = utils.get_test_data_upload(self.user, self.dataset, filename=utils.TEST_CSV_TYPES_FILENAME)
        self.dataset.import_data(self.user, upload)

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)

        dataset.reindex_data(self.user, typed_columns=[True for c in upload.columns])

        utils.wait()

        # Refresh from database
        dataset = Dataset.objects.get(id=self.dataset.id)
        task = dataset.current_task

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual([c['name'] for c in dataset.column_schema], ['text', 'date', 'integer', 'boolean', 'float', 'time', 'datetime', 'empty_column', ''])
        self.assertEqual([c['type'] for c in dataset.column_schema], ['unicode', 'date', 'int', 'bool', 'float', 'time', 'datetime', None, 'unicode'])
        self.assertEqual([c['indexed'] for c in dataset.column_schema], [True for c in upload.columns])
        self.assertEqual([c['indexed_name'] for c in dataset.column_schema], ['column_unicode_text', 'column_date_date', 'column_int_integer', 'column_bool_boolean', 'column_float_float', 'column_time_time', 'column_datetime_datetime', None, 'column_unicode_'])
        self.assertEqual([c['min'] for c in dataset.column_schema], [None, u'1920-01-01T00:00:00', 40, None, 1.0, u'9999-12-31T00:00:00', u'1971-01-01T04:14:00', None, None])
        self.assertEqual([c['max'] for c in dataset.column_schema], [None, u'1971-01-01T00:00:00', 164, None, 41800000.01, u'9999-12-31T14:57:13', u'2048-01-01T14:57:00', None, None])
        self.assertEqual(dataset.row_count, 5)
        self.assertEqual(dataset.locked, False)

        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_bool_boolean:true')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_unicode_text:"Chicago Tribune"')['response']['numFound'], 1)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_datetime_datetime:[1971-01-01T01:01:01Z TO NOW]')['response']['numFound'], 1)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_time_time:[9999-12-31T04:13:01Z TO *]')['response']['numFound'], 2)
        self.assertEqual(solr.query(settings.SOLR_DATA_CORE, 'column_date_date:[1971-01-01T00:00:00Z TO NOW]')['response']['numFound'], 1)

    def test_generate_typed_column_names_none(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        self.assertEqual([c['indexed_name'] for c in self.dataset.column_schema], [None, None, None, None])

    def test_generate_typed_column_names_some(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        typed_columns = [True, False, True, True]

        for i, c in enumerate(self.dataset.column_schema):
            self.dataset.column_schema[i]['indexed'] = typed_columns.pop(0)

        self.dataset.column_schema = update_indexed_names(self.dataset.column_schema)

        self.assertEqual([c['indexed_name'] for c in self.dataset.column_schema], ['column_int_id', None, 'column_unicode_last_name', 'column_unicode_employer'])

    def test_generate_typed_column_names_conflict(self):
        self.dataset.import_data(self.user, self.upload)

        utils.wait()

        typed_columns = [True, False, True, True]

        for i, c in enumerate(self.dataset.column_schema):
            self.dataset.column_schema[i]['name'] = 'test'
            self.dataset.column_schema[i]['indexed'] = typed_columns.pop(0)

        self.dataset.column_schema = update_indexed_names(self.dataset.column_schema)

        self.assertEqual([c['indexed_name'] for c in self.dataset.column_schema], ['column_int_test', None, 'column_unicode_test', 'column_unicode_test2'])

