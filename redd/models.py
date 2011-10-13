#!/usr/bin/env python

import os.path

from celery.result import AsyncResult
from django.conf import settings
from django.db import models

from redd.fields import JSONField
from redd.tasks import dataset_import_data
from redd.utils import infer_schema

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    filename = models.CharField(max_length=256,
        help_text='Filename as stored in PANDA.')
    original_filename = models.CharField(max_length=256,
        help_text='Filename as originally uploaded.')
    size = models.IntegerField(
        help_text='Size of the file in bytes.')

    def __unicode__(self):
        return self.filename

    def get_path(self):
        """
        Get the absolute path to this upload on disk.
        """
        return os.path.join(settings.MEDIA_ROOT, self.filename)

class Dataset(models.Model):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(max_length=256,
        help_text='User-supplied dataset name.')
    description = models.TextField(
        help_text='User-supplied dataset description.')
    data_upload = models.ForeignKey(Upload,
        help_text='The upload corresponding to the data file for this dataset.')
    schema = JSONField(null=True, blank=True,
        help_text='An ordered list of dictionaries describing the attributes of this dataset\'s columns.')
    current_task_id = models.CharField(max_length=255, null=True, blank=True,
        help_text='The currently executed or last finished task related to this dataset.') 

    def __unicode__(self):
        return self.name

    def get_current_task(self):
        """
        Get an AsyncResult object for the currently executing or last
        finished task.
        """
        if not self.current_task_id:
            return None

        return AsyncResult(self.current_task_id)

    def import_data(self):
        """
        Execute the data import task for this Dataset. Will use the currently configured schema.
        """
        result = dataset_import_data.apply_async(args=[self.id], queue='import', routing_key='import')
        self.current_task_id = result.task_id
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save to do fast, first-N type inference on the data and populated the schema.
        """
        if not self.schema:
            with open(self.data_upload.get_path(), 'r') as f:
                self.schema = infer_schema(f)

        super(Dataset, self).save(*args, **kwargs)

