#!/usr/bin/env python

from django.conf import settings
from django.db import models

from panda.models.base_upload import BaseUpload

class Export(BaseUpload):
    """
    A dataset exported to a file.
    """
    from panda.models.dataset import Dataset

    dataset = models.ForeignKey(Dataset, related_name='exports',
        help_text='The dataset this export is from.')

    file_root = settings.EXPORT_ROOT

    class Meta:
        app_label = 'panda'
        ordering = ['creation_date']

