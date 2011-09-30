#!/usr/bin/env python

from celery.decorators import task

@task(name='Import data')
def dataset_import_data(dataset_id, type_hypotheses):
    pass

