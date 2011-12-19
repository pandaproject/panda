#!/usr/bin/env python

import logging

from django.conf import settings
from celery.decorators import task

from redd import solr

@task(name='redd.tasks.dataset_purge_data')
def dataset_purge_data(dataset_slug):
    """
    Purge a dataset from Solr.
    """
    log = logging.getLogger('redd.tasks.dataset_purge_data')
    log.info('Beginning purge, dataset_slug: %s' % dataset_slug)

    solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % dataset_slug)

    log.info('Finished purge, dataset_slug: %s' % dataset_slug)

