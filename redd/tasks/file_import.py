#!/usr/bin/env python

from datetime import datetime
import logging
from math import floor

from celery.contrib.abortable import AbortableTask

from csvkit import CSVKitReader
from django.conf import settings

from redd import solr
from redd.utils import make_solr_row

SOLR_ADD_BUFFER_SIZE = 500

class DatasetImportTask(AbortableTask):
    """
    Task to import all data for a dataset from a data file.
    """
    name = 'redd.tasks.DatasetImportTask'

    def _count_lines(self, filename):
        """
        Efficiently count the number of lines in a file.
        """
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def run(self, dataset_slug, external_id_field_index, *args, **kwargs):
        """
        Execute import.
        """
        from redd.models import Dataset

        log = logging.getLogger('redd.tasks.DatasetImportTask')
        log.info('Beginning import, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)

        task_status = dataset.current_task
        task_status.status = 'STARTED' 
        task_status.start = datetime.now()
        task_status.message = 'Preparing to import'
        task_status.save()

        line_count = self._count_lines(dataset.data_upload.get_path())

        if self.is_aborted():
            task_status.status = 'ABORTED'
            task_status.end = datetime.now()
            task_status.message = 'Aborted during preperation'
            task_status.save()

            log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

            return

        f = open(dataset.data_upload.get_path(), 'r')

        dialect_params = {}

        # This code is absolutely terrifying
        # (Also, it works.)
        for k, v in dataset.dialect.items():
            if isinstance(v, basestring):
                dialect_params[k] = v.decode('string_escape')
            else:
                dialect_params[k] = v

        reader = CSVKitReader(f, **dialect_params)
        reader.next()

        add_buffer = []

        for i, row in enumerate(reader, start=1):
            external_id = None

            if external_id_field_index is not None:
                external_id = row[external_id_field_index]

            data = make_solr_row(dataset, row, external_id=external_id)

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)
                add_buffer = []

                task_status.message = '%.0f%% complete (estimated)' % floor(float(i) / float(line_count) * 100)
                task_status.save()

                if self.is_aborted():
                    task_status.status = 'ABORTED'
                    task_status.end = datetime.now()
                    task_status.message = 'Aborted after importing %.0f%% (estimated)' % floor(float(i) / float(line_count) * 100)
                    task_status.save()

                    log.warning('Import aborted, dataset_slug: %s' % dataset_slug)

                    return

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        task_status.message = '100% complete'
        task_status.save()

        dataset.row_count = i
        dataset.save()

        log.info('Finished import, dataset_slug: %s' % dataset_slug)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import Dataset, Notification, TaskStatus
        
        dataset = Dataset.objects.get(slug=args[0])
        task_status = TaskStatus.objects.get(id=self.request.id)

        notification = Notification(recipient=dataset.creator) 

        task_status.status = status
        task_status.message = 'Import complete'
        task_status.end = datetime.now()
        
        notification.message = 'Import of <strong>%s</strong> complete' % dataset.name

        if einfo:
            task_status.message = 'Import failed'
            task_status.traceback = u'\n'.join([einfo.traceback, unicode(retval)])
            
            notification.message = 'Import of %s failed' % dataset.name
            notification.type = 'error'
        
        notification.related_task = task_status
        notification.related_dataset = dataset
        
        task_status.save()
        notification.save()

        # If import failed, clear any data that might be staged for commit
        if task_status.status == 'FAILURE':
            solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % args[0], commit=True)

