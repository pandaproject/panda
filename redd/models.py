#!/usr/bin/env python

import os.path

from celery.result import AsyncResult
from django.conf import settings
from django.db import models

from redd.fields import JSONField
from redd.tasks import dataset_import_data
from redd.utils import infer_types

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    filename = models.CharField(max_length=256)
    original_filename = models.CharField(max_length=256)
    size = models.IntegerField()

    def __unicode__(self):
        return self.filename

    def get_path(self):
        return os.path.join(settings.PANDA_STORAGE_LOCATION, self.filename)

class Dataset(models.Model):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(max_length=256)
    data_upload = models.ForeignKey(Upload)
    schema = JSONField(null=True, blank=True)
    current_task_id = models.CharField(max_length=255, null=True, blank=True) 

    def __unicode__(self):
        return self.name

    def get_current_task(self):
        if not self.current_task_id:
            return None

        return AsyncResult(self.current_task_id)

    def import_data(self):
        result = dataset_import_data.delay(self.id)
        self.current_task_id = result.task_id
        self.save()

    def save(self, *args, **kwargs):
        if not self.schema:
            with open(self.data_upload.get_path(), 'r') as f:
                self.schema = infer_types(f)

        super(Dataset, self).save(*args, **kwargs)

