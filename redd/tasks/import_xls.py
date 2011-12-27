#!/usr/bin/env python

from datetime import datetime
import logging
from math import floor

from django.conf import settings
import xlrd

from redd import solr
from redd.tasks.import_file import ImportFileTask
from redd.utils import make_solr_row

SOLR_ADD_BUFFER_SIZE = 500

class ImportXLSTask(ImportFileTask):
    """
    Task to import all data for a dataset from an Excel XLS file.
    """
    name = 'redd.tasks.import.xls'

    def run(self, dataset_slug, external_id_field_index=None, *args, **kwargs):
        """
        Execute import.
        """
        from redd.models import Dataset

        log = logging.getLogger('redd.tasks.import.xls')
        log.info('Beginning import, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)

        task_status = dataset.current_task
        task_status.status = 'STARTED' 
        task_status.start = datetime.now()
        task_status.message = 'Preparing to import'
        task_status.save()

        f = open(dataset.data_upload.get_path(), 'rb')

        book = xlrd.open_workbook(file_contents=f.read())
        sheet = book.sheet_by_index(0)
        row_count = sheet.nrows
        
        add_buffer = []

        for i in range(1, row_count):
            values = sheet.row_values(i)

            external_id = None

            if external_id_field_index is not None:
                external_id = values[external_id_field_index]

            data = make_solr_row(dataset, values, external_id=external_id)

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)
                add_buffer = []

                task_status.message = '%.0f%% complete' % floor(float(i) / float(row_count) * 100)
                task_status.save()

                if self.is_aborted():
                    task_status.status = 'ABORTED'
                    task_status.end = datetime.now()
                    task_status.message = 'Aborted after importing %.0f%%' % floor(float(i) / float(row_count) * 100)
                    task_status.save()

                    log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

                    return

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        task_status.message = '100% complete'
        task_status.save()

        dataset.row_count = row_count - 1
        dataset.save()

        log.info('Finished import, dataset_slug: %s' % dataset_slug)

