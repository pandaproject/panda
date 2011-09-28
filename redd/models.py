#!/usr/bin/env python

from django.conf import settings
from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=256)
    filepath = models.FilePathField(path=settings.PANDA_STORAGE_LOCATION)

    def __unicode__(self):
        return self.name

