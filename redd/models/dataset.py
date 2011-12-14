#!/usr/bin/env python

from celery.contrib.abortable import AbortableAsyncResult
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver

from redd import solr, utils
from redd.fields import JSONField
from redd.models.category import Category
from redd.models.slugged_model import SluggedModel
from redd.models.task_status import TaskStatus
from redd.models.upload import Upload
from redd.tasks import DatasetImportTask, dataset_purge_data

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
    has_data = models.BooleanField(default=False,
        help_text='Has data for this dataset been imported or added via the API?')
    row_count = models.IntegerField(null=True, blank=True,
        help_text='The number of rows in this dataset. Only available once the dataset has data.')
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
    modified = models.BooleanField(default=False,
        help_text='Has this dataset ever been modified via the API?')

    class Meta:
        app_label = 'redd'
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

    def import_data(self, external_id_field_index=None):
        """
        Execute the data import task for this Dataset
        """
        self.current_task = TaskStatus.objects.create(
            task_name=DatasetImportTask.name)
        self.save()

        DatasetImportTask.apply_async([self.slug, external_id_field_index], task_id=self.current_task.id)

    def get_row(self, external_id):
        """
        Fetch a row from this dataset.
        """
        response = solr.query(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND external_id:%s' % (self.slug, external_id), limit=1)

        if len(response['response']['docs']) < 1:
            return None

        return response['response']['docs'][0]

    def add_row(self, data, external_id=None, commit=True, check_for_existing=True):
        """
        Add a row to this dataset.
        """
        if check_for_existing and external_id and self.get_row(external_id):
            raise ObjectDoesNotExist('A row with external_id %s already exists.' % external_id)

        solr_row = utils.make_solr_row(self, data, external_id=external_id)

        solr.add(settings.SOLR_DATA_CORE, [solr_row], commit=commit)

        if not self.sample_data:
            self.sample_data = []
        
        if len(self.sample_data) < 5:
            self.sample_data.append(data)

        # Enable searching
        if not self.has_data:
            self.has_data = True

        if not self.row_count:
            self.row_count = 0

        self.row_count += 1
        self.modified = True
        self.save()

        return solr_row

    def update_row(self, external_id, data, commit=True, check_for_existing=True):
        """
        Update a row in this dataset.
        """
        if check_for_existing and not self.get_row(external_id):
            raise ObjectDoesNotExist('A row with external_id %s does not exist.' % external_id)

        solr_row = utils.make_solr_row(self, data, external_id=external_id)

        solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND external_id:%s' % (self.slug, external_id), commit=True)
        solr.add(settings.SOLR_DATA_CORE, [solr_row], commit=commit)

        self.modified = True
        self.save()

        return solr_row

    def delete_row(self, external_id, commit=True, check_for_existing=True):
        """
        Delete a row in this dataset
        """
        if check_for_existing and not self.get_row(external_id):
            raise ObjectDoesNotExist('A row with external_id %s does not exist.' % external_id)

        solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND external_id:%s' % (self.slug, external_id), commit=commit)

        self.row_count -= 1

        if self.row_count == 0:
            self.has_data = False

        self.modified = True
        self.save()

    def _count_rows(self):
        """
        Count the number of rows currently stored in Solr for this Dataset.
        Useful for sanity checks.
        """
        return solr.query(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % self.slug)['response']['numFound']

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
        'slug': dataset.slug,
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
    dataset_purge_data.apply_async(args=[dataset.slug])
    solr.delete(settings.SOLR_DATASETS_CORE, 'slug:%s' % dataset.slug)

