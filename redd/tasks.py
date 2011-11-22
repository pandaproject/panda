#!/usr/bin/env python

from datetime import datetime
import logging
from math import floor
from uuid import uuid4

from celery.contrib.abortable import AbortableTask
from celery.decorators import task
from csvkit import CSVKitReader
from django.conf import settings
from django.utils import simplejson as json

from redd import solr

SOLR_ADD_BUFFER_SIZE = 500

class DatasetImportTask(AbortableTask):
    """
    Task to import all data for a dataset from a data file.
    """
    def _count_lines(self, filename):
        """
        Efficiently count the number of lines in a file.
        """
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def run(self, dataset_id, *args, **kwargs):
        """
        Execute import.
        """
        from redd.models import Dataset

        log = logging.getLogger('redd.tasks.DatasetImportTask')
        log.info('Beginning import, dataset_id: %i' % dataset_id)

        dataset = Dataset.objects.get(id=dataset_id)

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

            log.warning('Import aborted, dataset_id: %i' % dataset_id)

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
            data = {
                'id': unicode(uuid4()),
                'dataset_id': dataset.id,
                'row': i,
                'full_text': '\n'.join(row),
                'data': json.dumps(row)
            }

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(add_buffer)
                add_buffer = []

                task_status.message = '%.0f%% complete (estimated)' % floor(float(i) / float(line_count) * 100)
                task_status.save()

                if self.is_aborted():
                    task_status.status = 'ABORTED'
                    task_status.end = datetime.now()
                    task_status.message = 'Aborted after importing %.0f%% (estimated)' % floor(float(i) / float(line_count) * 100)
                    task_status.save()

                    log.warning('Import aborted, dataset_id: %i' % dataset_id)

                    return

        if add_buffer:
            solr.add(add_buffer)
            add_buffer = []

        solr.commit()

        task_status.message = '100% complete'
        task_status.save()

        dataset.imported = True
        dataset.row_count = i
        dataset.save()

        log.info('Finished import, dataset_id: %i' % dataset_id)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import Dataset, Notification, TaskStatus
        
        dataset = Dataset.objects.get(id=args[0])
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
            solr.delete('dataset_id:%i' % args[0], commit=True)

@task
def dataset_purge_data(dataset_id):
    """
    Purge a dataset from Solr.
    """
    log = logging.getLogger('redd.tasks.dataset_purge_data')
    log.info('Beginning purge, dataset_id: %i' % dataset_id)

    solr.delete('dataset_id:%i' % dataset_id)

    log.info('Finished purge, dataset_id: %i' % dataset_id)
    
