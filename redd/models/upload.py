#!/usr/bin/env python

from datetime import datetime
import os.path

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

from redd.fields import JSONField
from redd import utils

class Upload(models.Model):
    """
    A file uploaded to PANDA (either a table or metadata file).
    """
    from redd.models.dataset import Dataset
    
    filename = models.CharField(max_length=256,
        help_text='Filename as stored in PANDA.')
    original_filename = models.CharField(max_length=256,
        help_text='Filename as originally uploaded.')
    size = models.IntegerField(
        help_text='Size of the file in bytes.')
    creator = models.ForeignKey(User,
        help_text='The user who uploaded this file.')
    creation_date = models.DateTimeField(
        help_text='The date this file was uploaded.')
    dataset = models.ForeignKey(Dataset, related_name='uploads',
        help_text='The dataset this upload is associated with.')

    data_type = models.CharField(max_length=4, null=True, blank=True,
        help_text='The type of this file, if identified. An empty string indicates the type is no known.')
    dialect = JSONField(null=True,
        help_text = 'Description of the formatting of this file, if applicable.')
    columns = JSONField(null=True,
        help_text='An list of names for this uploads columns, if it contains data.')
    sample_data = JSONField(null=True,
        help_text = 'Example data from this file, if it contains data.')

    class Meta:
        app_label = 'redd'

    def __unicode__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.data_type is None:
            self.data_type = self._infer_data_type()

        if self.data_type:
            path = self.get_path()

            if self.dialect is None:
                self.dialect = utils.sniff_dialect(self.data_type, path)

            if self.columns is None:
                self.columns = utils.extract_column_names(self.data_type, path, self.dialect)

            if self.sample_data is None:
                self.sample_data = utils.sample_data(self.data_type, path, self.dialect)

        if not self.creation_date:
            self.creation_date = datetime.utcnow()

        super(Upload, self).save(*args, **kwargs)

    def get_path(self):
        """
        Get the absolute path to this upload on disk.
        """
        return os.path.join(settings.MEDIA_ROOT, self.filename)

    def _infer_data_type(self):
        """
        Get the data type of this file. Returns an empty string
        if the file is not a recognized type.
        """
        extension = os.path.splitext(self.filename)[1]

        if extension == '.csv':
            return 'csv' 
        elif extension == '.xls':
            return 'xls'
        elif extension == '.xlsx':
            return 'xlsx'

        return ''

