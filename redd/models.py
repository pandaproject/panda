#!/usr/bin/env python

from django.conf import settings
from django.db import models
from django.core.files.storage import FileSystemStorage

panda_storage = FileSystemStorage(location=settings.PANDA_STORAGE_LOCATION)

class Dataset(models.Model):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(max_length=256)
    data_upload = models.ForeignKey('Upload')

    def __unicode__(self):
        return self.name

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    filename = models.CharField(max_length=256)
    original_filename = models.CharField(max_length=256)
    size = models.IntegerField()

