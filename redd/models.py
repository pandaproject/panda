#!/usr/bin/env python

import os.path

from celery import states
from django.conf import settings
from django.db import models
from djcelery.models import TASK_STATE_CHOICES

from redd.fields import JSONField
from redd.tasks import DatasetImportTask, dataset_purge_data
from redd.utils import infer_schema, sample_data

class TaskStatus(models.Model):
    """
    An object to track the status of a Celery task, as the
    data available in AsyncResult is not sufficient.
    """
    task_id = models.CharField(max_length=255, primary_key=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default=states.PENDING, choices=TASK_STATE_CHOICES)
    message = models.CharField(max_length=255, blank=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    traceback = models.TextField(blank=True, null=True, default=None)

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
    sample_data = JSONField(null=True, blank=True,
        help_text='Example data from the first few rows of the dataset.')
    current_task = models.ForeignKey(TaskStatus, blank=True, null=True,
        help_text='The currently executed or last finished task related to this dataset.') 

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save to do fast, first-N type inference on the data and populated the schema.
        """
        if not self.schema:
            with open(self.data_upload.get_path(), 'r') as f:
                self.schema = infer_schema(f)

        if not self.sample_data:
            with open(self.data_upload.get_path(), 'r') as f:
                self.sample_data = sample_data(f)

        super(Dataset, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Purge data from Solr when a dataset is deleted.
        """
        dataset_id = self.id

        super(Dataset, self).delete(*args, **kwargs)
        dataset_purge_data.apply_async(args=[dataset_id])

    def import_data(self):
        """
        Execute the data import task for this Dataset. Will use the currently configured schema.
        """
        DatasetImportTask.delay(self.id)

