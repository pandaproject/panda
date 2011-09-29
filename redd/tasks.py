#!/usr/bin/env python

from celery.decorators import task

@task
def dataset_import(dataset_id):
    from redd.models import Dataset

    dataset = Dataset.objects.get(id=dataset_id)

    return dataset.data_upload.filename

