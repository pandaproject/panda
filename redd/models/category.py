#!/usr/bin/env python

from django.db import models

from redd.models.slugged_model import SluggedModel

class Category(SluggedModel):
    """
    A cateogory that contains Datasets.
    """
    name = models.CharField(max_length=64,
        help_text='Category name.')

    class Meta:
        app_label = 'redd'
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name

