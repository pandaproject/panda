#!/usr/bin/env python

import os.path

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    filename = models.CharField(max_length=256,
        help_text='Filename as stored in PANDA.')
    original_filename = models.CharField(max_length=256,
        help_text='Filename as originally uploaded.')
    size = models.IntegerField(
        help_text='Size of the file in bytes.')
    creator = models.ForeignKey(User,
        help_text='The user who uploaded this file.')

    class Meta:
        app_label = 'redd'

    def __unicode__(self):
        return self.filename

    def get_path(self):
        """
        Get the absolute path to this upload on disk.
        """
        return os.path.join(settings.MEDIA_ROOT, self.filename)

