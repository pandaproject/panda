#!/usr/bin/env python

from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=128)

