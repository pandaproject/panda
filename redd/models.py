#!/usr/bin/env python

import os.path
import re

from celery.contrib.abortable import AbortableAsyncResult
from celery import states
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from djcelery.models import TASK_STATE_CHOICES
from tastypie.models import ApiKey

from redd import solr, utils
from redd.fields import JSONField
from redd.tasks import DatasetImportTask, dataset_purge_data

NOTIFICATION_TYPE_CHOICES = (
    ('info', 'info'),
    ('warning', 'warning'),
    ('error', 'error')
)

@receiver(models.signals.post_save, sender=User)
def create_api_key(sender, **kwargs):
    """
    A signal for hooking up automatic ``ApiKey`` creation.
    """
    if kwargs.get('created') is True:
        ApiKey.objects.get_or_create(user=kwargs.get('instance'))

class SluggedModel(models.Model):
    """
    Extend this class to get a slug field and slug generated from a model
    field. We call the 'get_slug_text', '__unicode__' or '__str__'
    methods (in that order) on save() to get text to slugify. The slug may
    have numbers appended to make sure the slug is unique.
    """
    slug = models.SlugField(max_length=256)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()  
        
        super(SluggedModel, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Customized unique_slug function
        """
        if hasattr(self, 'get_slug_text') and callable(self.get_slug_text):
            slug_txt = self.get_slug_text()
        elif hasattr(self, '__unicode__'):
            slug_txt = unicode(self)
        elif hasattr(self, '__str__'):
            slug_txt = str(self)
        else:
            return

        slug = slugify(slug_txt)
        all_slugs = set(sl.values()[0] for sl in self.__class__.objects.values("slug"))

        if slug in all_slugs:
            counterFinder = re.compile(r'-\d+$')
            counter = 2
            slug = '%s-%i' % (slug, counter)

            while slug in all_slugs:
                slug = re.sub(counterFinder, '-%i' % counter, slug)
                counter += 1

        return slug 

class TaskStatus(models.Model):
    """
    An object to track the status of a Celery task, as the
    data available in AsyncResult is not sufficient.
    """
    task_name = models.CharField(max_length=255,
        help_text='Identifying name for this task.')
    status = models.CharField(max_length=50, default=states.PENDING, choices=TASK_STATE_CHOICES,
        help_text='Current state of this task.')
    message = models.CharField(max_length=255, blank=True,
        help_text='A human-readable message indicating the progress of this task.')
    start = models.DateTimeField(null=True,
        help_text='Date and time that this task began processing.')
    end = models.DateTimeField(null=True,
        help_text='Date and time that this task ceased processing (either complete or failed).')
    traceback = models.TextField(blank=True, null=True, default=None,
        help_text='Traceback that exited this task, if it failed.')

    class Meta:
        verbose_name = 'Task Status'
        verbose_name_plural = 'Task Statuses'

    def __unicode__(self):
        return u'%s (%i)' % (self.task_name, self.id)

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

    def __unicode__(self):
        return self.filename

    def get_path(self):
        """
        Get the absolute path to this upload on disk.
        """
        return os.path.join(settings.MEDIA_ROOT, self.filename)

class Category(SluggedModel):
    """
    A cateogory that contains Datasets.
    """
    name = models.CharField(max_length=64,
        help_text='Category name.')

    class Meta:
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.name

class Dataset(SluggedModel):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(max_length=256,
        help_text='User-supplied dataset name.')
    description = models.TextField(blank=True,
        help_text='User-supplied dataset description.')
    data_upload = models.ForeignKey(Upload, null=True, blank=True,
        help_text='The upload corresponding to the data file for this dataset.')
    schema = JSONField(null=True, default=None,
        help_text='An ordered list of dictionaries describing the attributes of this dataset\'s columns.')
    imported = models.BooleanField(default=False,
        help_text='Has this dataset been imported yet?')
    row_count = models.IntegerField(null=True, blank=True,
        help_text='The number of rows in this dataset. Only available once the dataset has been imported.')
    sample_data = JSONField(null=True, default=None,
        help_text='Example data from the first few rows of the dataset.')
    current_task = models.ForeignKey(TaskStatus, blank=True, null=True,
        help_text='The currently executed or last finished task related to this dataset.') 
    creation_date = models.DateTimeField(auto_now=True,
        help_text='The date this dataset was initially created.')
    creator = models.ForeignKey(User,
        help_text='The user who created this dataset.')
    dialect = JSONField(null=True, default=None,
        help_text='Description of the format of the input CSV.')
    categories = models.ManyToManyField(Category, related_name='datasets', blank=True, null=True,
        help_text='Categories containing this Dataset.')

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save to do fast, first-N type inference on the data and populated the schema.
        """
        if self.data_upload:
            if not self.dialect:
                with open(self.data_upload.get_path(), 'r') as f:
                    csv_dialect = utils.sniff(f)
                    self.dialect = {
                        'lineterminator': csv_dialect.lineterminator,
                        'skipinitialspace': csv_dialect.skipinitialspace,
                        'quoting': csv_dialect.quoting,
                        'delimiter': csv_dialect.delimiter,
                        'quotechar': csv_dialect.quotechar,
                        'doublequote': csv_dialect.doublequote
                    }

            if not self.schema:
                with open(self.data_upload.get_path(), 'r') as f:
                    self.schema = utils.infer_schema(f, self.dialect)

            if not self.sample_data:
                with open(self.data_upload.get_path(), 'r') as f:
                    self.sample_data = utils.sample_data(f, self.dialect)

        super(Dataset, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Purge data from Solr when a dataset is deleted.
        """
        # Cancel import if necessary 
        if self.current_task and self.current_task.end is None and self.current_task.task_name == 'redd.tasks.DatasetImportTask': 
            async_result = AbortableAsyncResult(self.current_task.id)
            async_result.abort()

        super(Dataset, self).delete(*args, **kwargs)

    def import_data(self):
        """
        Execute the data import task for this Dataset. Will use the currently configured schema.
        """
        self.current_task = TaskStatus.objects.create(
            task_name=DatasetImportTask.name)
        self.save()

        DatasetImportTask.apply_async([self.id], task_id=self.current_task.id)

    def add_row(self, data, row=None):
        """
        Add a row to this dataset.
        """
        solr_row = utils.make_solr_row(self, data, row)

        solr.add(settings.SOLR_DATA_CORE, [solr_row], commit=True)

        if not self.sample_data:
            self.sample_data = []
        
        if len(self.sample_data) < 5:
            self.sample_data.append({
                'row': row,
                'data': data
            })

        if not self.row_count:
            self.row_count = 0

        self.row_count += 1
        self.save()

        return solr_row

    def update_row(self, pk, data, row=None):
        """
        Update a row in this dataset.
        """
        solr_row = utils.make_solr_row(self, data, row, pk)

        solr.add(settings.SOLR_DATA_CORE, [solr_row], commit=True)

        return solr_row

@receiver(models.signals.post_save, sender=Dataset)
def on_dataset_save(sender, **kwargs):
    """
    When a Dataset is saved, update its metadata in Solr.
    """
    dataset = kwargs['instance']
    categories = [c.id for c in dataset.categories.all()] 

    full_text_data = [
        dataset.name,
        dataset.description
    ] 

    if dataset.data_upload:
        full_text_data.append(dataset.data_upload.original_filename)

    if dataset.schema:
        full_text_data.extend([s['column'] for s in dataset.schema])

    full_text = '\n'.join(full_text_data)

    solr.add(settings.SOLR_DATASETS_CORE, [{
        'id': dataset.id,
        'categories': categories,
        'full_text': full_text
    }], commit=True)

@receiver(models.signals.m2m_changed, sender=Dataset.categories.through)
def on_dataset_categories_change(sender, **kwargs):
    """
    When a dataset's categories changed, update it's metadata in Solr.

    TODO: This gets called WAY to frequently--is there a way to only
    call it when all changes have been made?
    """
    on_dataset_save(sender, **kwargs)

@receiver(models.signals.post_delete, sender=Dataset)
def on_dataset_delete(sender, **kwargs):
    """
    When a Dataset is deleted, purge its data and metadata from Solr
    """
    dataset = kwargs['instance']
    dataset_purge_data.apply_async(args=[dataset.id])
    solr.delete(settings.SOLR_DATASETS_CORE, 'id:%i' % dataset.id)

class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name='notifications',
        help_text='The user who should receive this notification.')
    message = models.TextField(
        help_text='The message to deliver.')
    type = models.CharField(max_length=16, choices=NOTIFICATION_TYPE_CHOICES, default='info',
        help_text='The type of message: info, warning or error')
    sent_at = models.DateTimeField(auto_now=True,
        help_text='When this notification was created')
    read_at = models.DateTimeField(null=True, blank=True, default=None,
        help_text='When this notification was read by the user.')
    related_task = models.ForeignKey(TaskStatus, null=True, default=None,
        help_text='A task related to this notification, if any.')
    related_dataset = models.ForeignKey(Dataset, null=True, default=None,
        help_text='A dataset related to this notification, if any.')

