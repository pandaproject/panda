#!/usr/bin/env python

import os.path

from django.core.files.storage import FileSystemStorage
from django.db import models

panda_storage = FileSystemStorage(location=os.path.expanduser('~/uploads'))

class Dataset(models.Model):
    name = models.CharField(max_length=128)
    table = models.ForeignKey('Upload')


