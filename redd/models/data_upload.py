#!/usr/bin/env python

import os.path

from django.conf import settings
from django.db import models

from redd import utils
from redd.fields import JSONField
from redd.models.base_upload import BaseUpload

class DataUpload(BaseUpload):
    """
    A data file uploaded to PANDA (either a table or metadata file).
    """
    from redd.models.dataset import Dataset

    dataset = models.ForeignKey(Dataset, related_name='data_uploads', null=True,
        help_text='The dataset this upload is associated with.')

    data_type = models.CharField(max_length=4, null=True, blank=True,
        help_text='The type of this file, if known.')
    dialect = JSONField(null=True,
        help_text='Description of the formatting of this file.')
    columns = JSONField(null=True,
        help_text='An list of names for this uploads columns.')
    sample_data = JSONField(null=True,
        help_text='Example data from this file.')
    imported = models.BooleanField(default=False,
        help_text='Has this upload ever been imported into its parent dataset.')
    
    file_root = settings.MEDIA_ROOT

    class Meta:
        app_label = 'redd'
        ordering = ['creation_date']

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

        super(DataUpload, self).save(*args, **kwargs)

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

