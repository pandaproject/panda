#!/usr/bin/env python

from celery.result import AsyncResult
from django.db import models

from redd.tasks import dataset_import

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    filename = models.CharField(max_length=256)
    original_filename = models.CharField(max_length=256)
    size = models.IntegerField()

    def __unicode__(self):
        return self.filename

class Dataset(models.Model):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(max_length=256)
    data_upload = models.ForeignKey(Upload)
    import_task_id = models.CharField(max_length=255, null=True, blank=True) 

    def __unicode__(self):
        return self.name

    def import_task(self):
        return AsyncResult(self.import_task_id)

    def save(self, *args, **kwargs):
        # Save to get id
        super(Dataset, self).save(*args, **kwargs)

        # Kick off data processing
        result = dataset_import.delay(self.id)
        self.import_task_id = result.task_id
        
        # Stash task id
        super(Dataset, self).save(*args, **kwargs)

        print self.import_task().status

