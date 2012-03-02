#!/usr/bin/env python

import datetime
import logging
from math import floor
from types import NoneType

from csvkit import CSVKitReader
from django.conf import settings

from panda import solr, utils
from panda.exceptions import DataImportError, TypeCoercionError
from panda.tasks.import_file import ImportFileTask 
from panda.utils.typecoercion import coerce_type

SOLR_ADD_BUFFER_SIZE = 500

TYPE_NAMES_MAPPING = {
    'unicode': unicode,
    'int': int,
    'bool': bool,
    'float': float,
    'datetime': datetime.datetime,
    'NoneType': NoneType
}

class ImportCSVTask(ImportFileTask):
    """
    Task to import all data for a dataset from a CSV.
    """
    name = 'panda.tasks.import.csv'

    def _count_lines(self, filename):
        """
        Efficiently count the number of lines in a file.
        """
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def run(self, dataset_slug, upload_id, external_id_field_index=None, *args, **kwargs):
        """
        Execute import.
        """
        from panda.models import Dataset, DataUpload
        
        log = logging.getLogger(self.name)
        log.info('Beginning import, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)
        upload = DataUpload.objects.get(id=upload_id)

        task_status = dataset.current_task
        self.task_start(task_status, 'Preparing to import')

        line_count = self._count_lines(upload.get_path())

        if self.is_aborted():
            self.task_abort(task_status, 'Aborted during preperation')

            log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

            return

        f = open(upload.get_path(), 'r')

        reader = CSVKitReader(f, encoding=upload.encoding, **upload.dialect_as_parameters())
        reader.next()

        add_buffer = []

        i = 0

        while True:
            # The row number which is about to be read, for error handling and indexing
            i += 1

            try:
                row = reader.next()
            except StopIteration:
                i -= 1
                break
            except UnicodeDecodeError:
                raise DataImportError('This CSV file contains characters that are not %s encoded in or after row %i. You need to re-upload this file and input the correct encoding in order to import data from this file.' % (upload.encoding, i))

            external_id = None

            if external_id_field_index is not None:
                external_id = row[external_id_field_index]

            data = utils.solr.make_data_row(dataset, row, external_id=external_id)

            # Generate typed column data
            for n, c in enumerate(dataset.columns):
                if dataset.typed_columns[n]:
                    type_name = dataset.column_types[n]

                    try:
                        value = coerce_type(row[n], TYPE_NAMES_MAPPING[type_name])
                        data[dataset.typed_column_names[n]] = value
                    except TypeCoercionError, e:
                        # TODO: log here
                        pass

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)

                add_buffer = []

                self.task_update(task_status, '%.0f%% complete (estimated)' % floor(float(i) / float(line_count) * 100))

                if self.is_aborted():
                    self.task_abort(task_status, 'Aborted after importing %.0f%% (estimated)' % floor(float(i) / float(line_count) * 100))

                    log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

                    return

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        f.close()

        self.task_update(task_status, '100% complete')

        # Refresh dataset from database so there is no chance of crushing changes made since the task started
        dataset = Dataset.objects.get(slug=dataset_slug)

        if not dataset.row_count:
            dataset.row_count = i
        else:
            dataset.row_count += i

        dataset.save()

        # Refres
        upload = DataUpload.objects.get(id=upload_id)

        upload.imported = True
        upload.save()

        log.info('Finished import, dataset_slug: %s' % dataset_slug)

