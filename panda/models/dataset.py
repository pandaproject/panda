#!/usr/bin/env python

from urllib import unquote

from django.conf import settings
from django.db import models
from django.utils.timezone import now 
from django.utils.translation import ugettext_lazy as _

from panda import solr, utils
from panda.exceptions import DataImportError, DatasetLockedError
from panda.fields import JSONField
from panda.models.category import Category
from panda.models.slugged_model import SluggedModel
from panda.models.task_status import TaskStatus
from panda.models.user_proxy import UserProxy
from panda.tasks import get_import_task_type_for_upload, ExportCSVTask, PurgeDataTask, ReindexTask 
from panda.utils.column_schema import make_column_schema, update_indexed_names
from panda.utils.typecoercion import DataTyper

class Dataset(SluggedModel):
    """
    A PANDA dataset (one table & associated metadata).
    """
    name = models.CharField(_('name'), max_length=256,
        help_text=_('User-supplied dataset name.'))
    description = models.TextField(_('description'), blank=True,
        help_text=_('User-supplied dataset description.'))
    # related_uploads =  models.ToMany(RelatedUpload, null=True)
    # data_uploads =  models.ToMany(DataUpload, null=True)
    initial_upload = models.ForeignKey('DataUpload', null=True, blank=True, related_name='initial_upload_for',
        help_text=_('The data upload used to create this dataset, if any was used.'),
        verbose_name=_('initial_upload'))
    column_schema = JSONField(_('column_schema'), null=True, default=None,
        help_text=_('Metadata about columns.'))
    sample_data = JSONField(_('sample_data'), null=True, default=None,
        help_text=_('Example data rows from the dataset.'))
    row_count = models.IntegerField(_('row_count'), null=True, blank=True,
        help_text=_('The number of rows in this dataset. Null if no data has been added/imported.'))
    current_task = models.ForeignKey(TaskStatus, blank=True, null=True,
        help_text=_('The currently executed or last finished task related to this dataset.'),
        verbose_name=_('current_task')) 
    creation_date = models.DateTimeField(_('creation_date'), null=True,
        help_text=_('The date this dataset was initially created.'))
    creator = models.ForeignKey(UserProxy, related_name='datasets',
        help_text=_('The user who created this dataset.'),
        verbose_name=_('creator'))
    categories = models.ManyToManyField(Category, related_name='datasets', blank=True, null=True,
        help_text=_('Categories containing this Dataset.'),
        verbose_name=_('categories'))
    last_modified = models.DateTimeField(_('last_modified'), null=True, blank=True, default=None,
        help_text=_('When, if ever, was this dataset last modified via the API?'))
    last_modification = models.TextField(_('last_modification'), null=True, blank=True, default=None,
        help_text=_('Description of the last modification made to this Dataset.'))
    last_modified_by = models.ForeignKey(UserProxy, null=True, blank=True,
        help_text=_('The user, if any, who last modified this dataset.'),
        verbose_name=_('last_modified_by'))
    locked = models.BooleanField(_('locked'), default=False,
        help_text=_('Is this table locked for writing?'))
    locked_at = models.DateTimeField(_('locked_at'), null=True, default=None,
        help_text=_('Time this dataset was last locked.'))
    related_links = JSONField(default=[])

    class Meta:
        app_label = 'panda'
        ordering = ['-creation_date']
        verbose_name = _('Dataset')
        verbose_name_plural = _('Datasets')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save the date of creation.
        """
        if not self.creation_date:
            self.creation_date = now()

        super(Dataset, self).save(*args, **kwargs)

    def lock(self):
        """
        Obtain an editing lock on this dataset.
        """
        # Ensure latest state has come over from the database
        before_lock = self.__class__.objects.get(pk=self.pk)
        self.locked = before_lock.locked
        self.locked_at = before_lock.locked_at

        if self.locked:
            # Already locked
            raise DatasetLockedError(_('This dataset is currently locked by another process.'))

        new_locked_at = now()

        self.locked = True
        self.locked_at = new_locked_at

        self.save()

        # Refresh from database
        after_lock = Dataset.objects.get(id=self.id)
        self.locked = after_lock.locked
        self.locked_at = after_lock.locked_at

        if self.locked_at != new_locked_at:
            # Somebody else got the lock
            raise DatasetLockedError(_('This dataset is currently locked by another process.'))

    def unlock(self):
        """
        Unlock this dataset so it can be edited.
        """
        self.locked = False
        self.lock_id = None

        self.save()

    def update_full_text(self, commit=True):
        """
        Update the full-text search metadata for this dataset stored in Solr.
        """
        category_ids = []

        full_text_data = [
            unquote(self.name),
            unquote(self.description),
            '%s %s' % (self.creator.first_name, self.creator.last_name),
            self.creator.email
        ]

        for category in self.categories.all():
            category_ids.append(category.id)
            full_text_data.append(category.name)

        if not category_ids:
            category_ids.append(settings.PANDA_UNCATEGORIZED_ID)
            full_text_data.append(settings.PANDA_UNCATEGORIZED_NAME)

        for data_upload in self.data_uploads.all():
            full_text_data.append(data_upload.original_filename)

        for related_upload in self.related_uploads.all():
            full_text_data.append(related_upload.original_filename)

        if self.column_schema is not None:
            full_text_data.extend([c['name'] for c in self.column_schema])

        full_text = u'\n'.join(map(unicode, full_text_data)) # convert any i18n proxies into strings

        solr.add(settings.SOLR_DATASETS_CORE, [{
            'slug': self.slug,
            'creation_date': self.creation_date.isoformat() + 'Z',
            'categories': category_ids,
            'full_text': full_text
        }], commit=commit)

    def delete(self, *args, **kwargs):
        """
        Cancel any in progress task.
        """
        # Cancel import if necessary 
        if self.current_task:
            self.current_task.request_abort()

        # Manually delete related uploads so their delete method is called
        for upload in self.data_uploads.all():
            upload.delete(skip_purge=True, force=True)

        for upload in self.related_uploads.all():
            upload.delete()

        # Cleanup data in Solr
        PurgeDataTask.apply_async(args=[self.slug])
        solr.delete(settings.SOLR_DATASETS_CORE, 'slug:%s' % self.slug)

        super(Dataset, self).delete(*args, **kwargs)

    def import_data(self, user, upload, external_id_field_index=None, schema_overrides = {}):
        """
        Import data into this ``Dataset`` from a given ``DataUpload``.
        """
        self.lock()

        try:
            if upload.imported:
                raise DataImportError(_('This file has already been imported.'))

            task_type = get_import_task_type_for_upload(upload)

            if not task_type:
                # This is normally caught on the client.
                raise DataImportError(_('This file type is not supported for data import.'))
            
            if self.column_schema:
                # This is normally caught on the client.
                if upload.columns != [c['name'] for c in self.column_schema]:
                    raise DataImportError(_('The columns in this file do not match those in the dataset.'))
            else:
                self.column_schema = make_column_schema(upload.columns, types=upload.guessed_types, overrides=schema_overrides)

            if self.sample_data is None:
                self.sample_data = upload.sample_data

            # If this is the first import and the API hasn't been used, save that information
            if self.initial_upload is None and self.row_count is None:
                self.initial_upload = upload

            self.current_task = TaskStatus.objects.create(
                task_name=task_type.name,
                task_description=_('Import data from %(filename)s into %(slug)s.') \
                    % {'filename': upload.filename, 'slug': self.slug},
                creator=user
            )
            self.save()

            task_type.apply_async(
                args=[self.slug, upload.id],
                kwargs={ 'external_id_field_index': external_id_field_index },
                task_id=self.current_task.id
            )
        except:
            self.unlock()
            raise

    def reindex_data(self, user, typed_columns=None, column_types=None):
        """
        Reindex the data currently stored for this ``Dataset``.
        """
        self.lock()
        
        task_type = ReindexTask

        try:
            typed_column_count = 0

            if typed_columns:
                for i, t in enumerate(typed_columns):
                    self.column_schema[i]['indexed'] = t
                    
                    if t:
                        typed_column_count += 1

            if column_types:
                for i, t in enumerate(column_types):
                    self.column_schema[i]['type'] = t

            self.column_schema = update_indexed_names(self.column_schema)

            self.current_task = TaskStatus.objects.create(
                task_name=task_type.name,
                task_description=_('Reindex %(slug)s with %(typed_column_count)i column filters.') \
                     % {'slug': self.slug, 'typed_column_count': typed_column_count}, 
                creator=user
            )

            self.save()

            task_type.apply_async(
                args=[self.slug],
                kwargs={},
                task_id=self.current_task.id
            )
        except:
            self.unlock()
            raise

    def export_data(self, user, query=None, filename=None):
        """
        Execute the data export task for this ``Dataset``.
        """
        task_type = ExportCSVTask

        if query:
            description = _('Export search results for "%(query)s" in %(slug)s.') \
                % {'query': query, 'slug': self.slug}
        else:
            description = _('Exporting data in %s.') % self.slug

        self.current_task = TaskStatus.objects.create(
            task_name=task_type.name,
            task_description=description,
            creator=user
        )

        self.save()

        task_type.apply_async(
            args=[self.slug],
            kwargs={ 'query': query, 'filename': filename },
            task_id=self.current_task.id
        )

    def get_row(self, external_id):
        """
        Fetch a row from this dataset.
        """
        response = solr.query(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND external_id:%s' % (self.slug, external_id), limit=1)

        if len(response['response']['docs']) < 1:
            return None

        return response['response']['docs'][0]

    def add_row(self, user, data, external_id=None):
        """
        Add (or overwrite) a row to this dataset.
        """
        self.lock()

        try:
            data_typer = DataTyper(self.column_schema)

            solr_row = utils.solr.make_data_row(self, data, external_id=external_id)
            solr_row = data_typer(solr_row, data)

            solr.add(settings.SOLR_DATA_CORE, [solr_row], commit=True)

            self.schema = data_typer.schema

            if not self.sample_data:
                self.sample_data = []
            
            if len(self.sample_data) < 5:
                self.sample_data.append(data)

            old_row_count = self.row_count
            self.row_count = self._count_rows()
            added = self.row_count - (old_row_count or 0)
            self.last_modified = now()
            self.last_modified_by = user
            self.last_modification = _('1 row %s') % ('added' if added else 'updated')
            self.save()

            return solr_row
        finally:
            self.unlock()

    def add_many_rows(self, user, data):
        """
        Shortcut for adding rows in bulk. 

        ``data`` must be an array of tuples in the format (data_array, external_id)
        """
        self.lock()

        try:
            data_typer = DataTyper(self.column_schema)

            solr_rows = [utils.solr.make_data_row(self, d[0], external_id=d[1]) for d in data]
            solr_rows = [data_typer(s, d[0]) for s, d in zip(solr_rows, data)]

            solr.add(settings.SOLR_DATA_CORE, solr_rows, commit=True)
            
            self.schema = data_typer.schema

            if not self.sample_data:
                self.sample_data = []
            
            if len(self.sample_data) < 5:
                needed = 5 - len(self.sample_data)
                self.sample_data.extend([d[0] for d in data[:needed]])

            old_row_count = self.row_count
            self.row_count = self._count_rows()
            added = self.row_count - (old_row_count or 0)
            updated = len(data) - added
            self.last_modified = now()
            self.last_modified_by = user

            if added and updated: 
                self.last_modification = _('%(added)i rows added and %(updated)i updated') \
                    % {'added': added, 'updated': updated}
            elif added:
                self.last_modification = _('%i rows added') % added
            else:
                self.last_modification = _('%i rows updated') % updated

            self.save()

            return solr_rows
        finally:
            self.unlock()
        
    def delete_row(self, user, external_id):
        """
        Delete a row in this dataset.
        """
        self.lock()

        try:
            solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s AND external_id:%s' % (self.slug, external_id), commit=True)
        
            self.row_count = self._count_rows()
            self.last_modified = now()
            self.last_modified_by = user
            self.last_modification = _('1 row deleted')
            self.save()
        finally:
            self.unlock()

    def delete_all_rows(self, user,):
        """
        Delete all rows in this dataset.
        """
        self.lock()

        try:
            solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % self.slug, commit=True)

            old_row_count = self.row_count
            self.row_count = 0
            self.last_modified = now()
            self.last_modification = _('All %i rows deleted') % old_row_count or 0
            self.save()
        finally:
            self.unlock()

    def _count_rows(self):
        """
        Count the number of rows currently stored in Solr for this Dataset.
        Useful for sanity checks.
        """
        return solr.query(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % self.slug)['response']['numFound']

