#!/usr/bin/env python

import os.path

from django.db import models
from django.utils.timezone import now 
from django.utils.translation import ugettext_lazy as _

from panda.models.user_proxy import UserProxy

class BaseUpload(models.Model):
    """
    Base class for any file uploaded to PANDA.
    """
    filename = models.CharField(_('filename'), 
        max_length=256,
        help_text=_('Filename as stored in PANDA.'))
    original_filename = models.CharField(_('original_filename'), 
        max_length=256,
        help_text=_('Filename as originally uploaded.'))
    size = models.IntegerField(_('size'),
        help_text=_('Size of the file in bytes.'))
    creator = models.ForeignKey(UserProxy,
        help_text=_('The user who uploaded this file.'),
        verbose_name=_('creator'))
    creation_date = models.DateTimeField(_('creation_date'),
        help_text=_('The date this file was uploaded.'))
    title = models.TextField(_('title'),
        max_length=256,
        help_text=_('A user-friendly name for this file.'))

    class Meta:
        app_label = 'panda'
        abstract = True

    def __unicode__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = now()

        if not self.title:
            self.title = self.original_filename

        super(BaseUpload, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        When deleting an upload, it will attempt to clean
        up its own associated files.
        """
        try:
            os.remove(self.get_path())
        except:
            pass

        super(BaseUpload, self).delete(*args, **kwargs)

    def get_path(self):
        """
        Get the absolute path to this upload on disk.
        """
        return os.path.join(self.file_root, self.filename)

