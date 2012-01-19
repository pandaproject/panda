#!/usr/bin/env python

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from redd import solr
from redd.models.slugged_model import SluggedModel

class Category(SluggedModel):
    """
    A category that contains Datasets.
    """
    name = models.CharField(max_length=64,
        help_text='Category name.')

    class Meta:
        app_label = 'redd'
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name

