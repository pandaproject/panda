#!/usr/bin/env python

import logging
from math import floor

from django.conf import settings
import xlrd

from redd import solr, utils
from redd.tasks.import_file import ImportFileTask

SOLR_ADD_BUFFER_SIZE = 500

class ImportXLSTask(ImportFileTask):
    """
    Task to import all data for a dataset from an Excel XLS file.
    """
    name = 'redd.tasks.import.xls'

    def run(self, dataset_slug, upload_id, external_id_field_index=None, *args, **kwargs):
        """
        Execute import.
        """
        from redd.models import Dataset, Upload
        
        log = logging.getLogger(self.name)
        log.info('Beginning import, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)
        upload = Upload.objects.get(id=upload_id)

        task_status = dataset.current_task
        self.task_start(task_status, 'Preparing to import')

        book = xlrd.open_workbook(upload.get_path(), on_demand=True)
        sheet = book.sheet_by_index(0)
        row_count = sheet.nrows
        
        add_buffer = []

        for i in range(1, row_count):
            values = sheet.row_values(i)
            types = sheet.row_types(i)

            normal_values = []

            for v, t in zip(values, types):
                if t == xlrd.biffh.XL_CELL_DATE:
                    v = utils.xls.normalize_date(v, book.datemode)
                elif t == xlrd.biffh.XL_CELL_NUMBER:
                    if v % 1 == 0:
                        v = int(v)

                normal_values.append(unicode(v))

            external_id = None

            if external_id_field_index is not None:
                external_id = values[external_id_field_index]

            data = utils.solr.make_data_row(dataset, values, external_id=external_id)

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)
                add_buffer = []

                task_status.message = '%.0f%% complete' % floor(float(i) / float(row_count) * 100)
                task_status.save()

                if self.is_aborted():
                    self.task_abort(self.task_status, 'Aborted after importing %.0f%%' % floor(float(i) / float(row_count) * 100))

                    log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

                    return

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        self.task_update(task_status, '100% complete')

        dataset.row_count = row_count - 1
        dataset.save()

        log.info('Finished import, dataset_slug: %s' % dataset_slug)

