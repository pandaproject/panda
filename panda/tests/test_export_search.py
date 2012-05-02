#!/usr/bin/env python

import os.path
from zipfile import ZipFile

from django.conf import settings
from django.test import TransactionTestCase

from panda.models import TaskStatus
from panda.tasks import ExportSearchTask
from panda.tests import utils

class TestExportSearch(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.dataset2 = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_export_query_csv(self):
        self.dataset.import_data(self.user, self.upload)
        self.dataset2.import_data(self.user, self.upload)

        task_type = ExportSearchTask

        task = TaskStatus.objects.create(task_name=task_type.name, creator=self.user)

        task_type.apply_async(
            args=['tribune', task.id],
            kwargs={ 'filename': 'test' },
            task_id=task.id
        )

        # Refresh from database
        task = TaskStatus.objects.get(id=task.id)

        self.assertEqual(task.status, 'SUCCESS')
        self.assertNotEqual(task.start, None)
        self.assertNotEqual(task.end, None)
        self.assertEqual(task.traceback, None)

        self.assertEqual(os.path.exists(os.path.join(settings.EXPORT_ROOT, 'test.zip')), True)
        self.assertEqual(os.path.exists(os.path.join(settings.EXPORT_ROOT, 'test')), False)

        zipfile = ZipFile(os.path.join(settings.EXPORT_ROOT, 'test.zip'))

        expected_filenames = ['contributors.csv', 'contributors-2.csv']

        self.assertEqual(set(zipfile.namelist()), set(expected_filenames))

        for filename in expected_filenames:
            with zipfile.open(filename) as f:
                self.assertEqual('id,first_name,last_name,employer\n', f.next())
                self.assertEqual('1,Brian,Boyer,Chicago Tribune\n', f.next())
                self.assertEqual('2,Joseph,Germuska,Chicago Tribune\n', f.next())
                
                with self.assertRaises(StopIteration):
                    f.next()

