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
        log = logging.getLogger(self.name)
        log.info('Beginning purge, dataset_slug: %s' % dataset_slug)

        q = 'dataset_slug:%s' % dataset_slug

        if data_upload_id:
            q += ' data_upload_id:%i' % data_upload_id

        solr.delete(settings.SOLR_DATA_CORE, q)

        log.info('Finished purge, dataset_slug: %s' % dataset_slug)

