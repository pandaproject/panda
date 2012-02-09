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

    def run(self, dataset_slug):
        log = logging.getLogger('panda.tasks.purge.data')
        log.info('Beginning purge, dataset_slug: %s' % dataset_slug)

        solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % dataset_slug)

        log.info('Finished purge, dataset_slug: %s' % dataset_slug)

