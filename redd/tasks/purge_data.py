#!/usr/bin/env python

import logging

from django.conf import settings
from celery.task import Task

from redd import solr

class PurgeDataTask(Task):
    """
    Purge a dataset from Solr.
    """
    name = 'redd.tasks.PurgeDataTask'

    def run(self, dataset_slug):
        log = logging.getLogger('redd.tasks.PurgeDataTask')
        log.info('Beginning purge, dataset_slug: %s' % dataset_slug)

        solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % dataset_slug)

        log.info('Finished purge, dataset_slug: %s' % dataset_slug)

