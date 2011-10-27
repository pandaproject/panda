#!/usr/bin/env python

from datetime import datetime
import json
import logging
from math import floor
from uuid import uuid4

from celery.decorators import task
from celery.task import Task
from django.conf import settings
from sunburnt import SolrInterface

from csvkit import CSVKitReader

SOLR_ADD_BUFFER_SIZE = 500

class DatasetImportTask(Task):
    """
    Import a dataset into Solr.
    """
    def __call__(self, dataset_id, *args, **kwargs):
        """
        Setup task tracking.
        """
        from redd.models import Dataset, TaskStatus

        task_status = TaskStatus.objects.create(
            task_id=self.request.id,
            task_name=self.name)

        dataset = Dataset.objects.get(id=dataset_id)
        dataset.current_task = task_status
        dataset.save()

        return self.run(dataset_id, *args, **kwargs)

    def _count_lines(self, filename):
        """
        Efficiently count the number of lines in a file.
        """
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def run(self, dataset_id):
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

        solr = SolrInterface(settings.SOLR_ENDPOINT)
            
        reader = CSVKitReader(open(dataset.data_upload.get_path(), 'r'))
        reader.next()

        add_buffer = []

        for i, row in enumerate(reader, start=1):
            data = {
                'id': uuid4(),
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

        if add_buffer:
            solr.add(add_buffer)
            add_buffer = []
        
        solr.commit()

        dataset.row_count = i
        dataset.save()

        log.info('Finished import, dataset_id: %i' % dataset_id)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import TaskStatus

        task_status = TaskStatus.objects.get(task_id=self.request.id)

        task_status.status = status
        task_status.message = 'Import complete'
        task_status.end = datetime.now()

        if einfo:
            task_status.traceback = einfo.traceback

        task_status.save()

#tasks.register(DatasetImportTask)

@task(name='Purge data')
def dataset_purge_data(dataset_id):
    """
    Purge a dataset from Solr.
    """
    log = logging.getLogger('redd.tasks.dataset_purge_data')
    log.info('Beginning purge, dataset_id: %i' % dataset_id)

    solr = SolrInterface(settings.SOLR_ENDPOINT)
    solr.delete(queries='dataset_id: %i' % dataset_id, commit=True)

    log.info('Finished purge, dataset_id: %i' % dataset_id)
    
