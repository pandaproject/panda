#!/usr/bin/env python

import logging

from django.conf import settings
from celery.task import Task

from panda import solr

class PurgeDataTask(Task):
    """
    Purge a dataset from Solr.
    """
    name = 'panda.tasks.purge.data'

    def run(self, dataset_slug, data_upload_id=None):
        from panda.models import Dataset

        log = logging.getLogger(self.name)
        log.info('Beginning purge, dataset_slug: %s' % dataset_slug)

        if data_upload_id:
            q = 'data_upload_id:%i' % data_upload_id
        else:
            q = 'dataset_slug:%s' % dataset_slug

        solr.delete(settings.SOLR_DATA_CORE, q)

        try:
            # If the dataset hasn't been deleted, update its row count
            dataset = Dataset.objects.get(slug=dataset_slug)
            dataset.row_count = dataset._count_rows()
            dataset.save()
        except Dataset.DoesNotExist:
            pass

        log.info('Finished purge, dataset_slug: %s' % dataset_slug)

