#!/usr/bin/env python

from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.slugged_model import SluggedModel

class Category(SluggedModel):
    """
    A category that contains Datasets.
    """
    name = models.CharField(_('name'),
        max_length=64,
        help_text=_('Category name.'))

    class Meta:
        app_label = 'panda'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.name

