#!/usr/bin/env python

from celery.decorators import task

@task(name='Import data')
def dataset_import_data(dataset_id):
    from redd.models import Dataset

    dataset = Dataset.objects.get(id=dataset_id)
    schema = dataset.schema

    # TKTK

    return schema

