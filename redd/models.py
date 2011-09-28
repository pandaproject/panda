#!/usr/bin/env python

from django.db import models

from redd.storage import panda_storage 

class Dataset(models.Model):
    name = models.CharField(max_length=128)
    table = models.ForeignKey('Upload')

class Upload(models.Model):
    file = models.FileField(upload_to='uploads', storage=panda_storage)

