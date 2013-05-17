#!/usr/bin/env python

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.base_upload import BaseUpload

class Export(BaseUpload):
    """
    A dataset exported to a file.
    """
    from panda.models.dataset import Dataset

    dataset = models.ForeignKey(Dataset, related_name='exports', null=True,
        help_text=_('The dataset this export is from.'),
        verbose_name=_('dataset'))

    file_root = settings.EXPORT_ROOT

    class Meta:
        app_label = 'panda'
        ordering = ['creation_date']
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')

