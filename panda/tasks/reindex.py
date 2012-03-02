#!/usr/bin/env python

from datetime import datetime
import logging
from math import floor
from types import NoneType

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from django.utils import simplejson as json
from livesettings import config_value

from panda import solr, utils
from panda.exceptions import TypeCoercionError
from panda.utils.mail import send_mail
from panda.utils.typecoercion import coerce_type

SOLR_READ_BUFFER_SIZE = 500
SOLR_ADD_BUFFER_SIZE = 500

TYPE_NAMES_MAPPING = {
    'unicode': unicode,
    'int': int,
    'bool': bool,
    'float': float,
    'datetime': datetime,
    'NoneType': NoneType
}

class ReindexTask(AbortableTask):
    """
    Task to import all data for a dataset from a CSV.
    """
    name = 'panda.tasks.reindex'

    def task_start(self, task_status, message):
        """
        Mark that task has begun.
        """
        task_status.status = 'STARTED' 
        task_status.start = datetime.utcnow()
        task_status.message = message 
        task_status.save()

    def task_update(self, task_status, message):
        """
        Update task status message.
        """
        task_status.message = message 
        task_status.save()

    def task_abort(self, task_status, message):
        """
        Mark that task has aborted.
        """
        task_status.status = 'ABORTED'
        task_status.end = datetime.utcnow()
        task_status.message = message
        task_status.save()

    def task_complete(self, task_status, message):
        """
        Mark that task has completed.
        """
        task_status.status = 'SUCCESS'
        task_status.end = datetime.utcnow()
        task_status.message = message
        task_status.save()

    def task_exception(self, task_status, message, formatted_traceback):
        """
        Mark that task raised an exception
        """
        task_status.status = 'FAILURE'
        task_status.end = datetime.utcnow()
        task_status.message = message 
        task_status.traceback = formatted_traceback
        task_status.save()

    def run(self, dataset_slug, external_id_field_index=None, *args, **kwargs):
        """
        Execute reindex.
        """
        from panda.models import Dataset
        
        log = logging.getLogger(self.name)
        log.info('Beginning reindex, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)

        task_status = dataset.current_task
        self.task_start(task_status, 'Preparing to reindex')

        if self.is_aborted():
            self.task_abort(task_status, 'Aborted during preperation')

            log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

            return

        read_buffer = []
        add_buffer = []

        i = 0

        while i < dataset.row_count:
            if not read_buffer:
                query = 'dataset_slug: %s' % (dataset.slug)
                response = solr.query(settings.SOLR_DATA_CORE, query, limit=SOLR_READ_BUFFER_SIZE, offset=i, sort='id asc')
                read_buffer = response['response']['docs']

            data = read_buffer.pop(0)
            row = json.loads(data['data'])


            new_data = utils.solr.make_data_row(dataset, row)
            new_data['id'] = data['id'] 

            # Generate typed column data
            for n, c in enumerate(dataset.columns):
                if dataset.typed_columns[n]:
                    type_name = dataset.column_types[n]

                    try:
                        value = coerce_type(row[n], TYPE_NAMES_MAPPING[type_name])
                        new_data[dataset.typed_column_names[n]] = value
                    except TypeCoercionError, e:
                        # TODO: log here
                        pass

            add_buffer.append(new_data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)

                add_buffer = []

                self.task_update(task_status, '%.0f%% complete' % floor(float(i) / float(dataset.row_count) * 100))

                if self.is_aborted():
                    self.task_abort(task_status, 'Aborted after reindexing %.0f%%' % floor(float(i) / float(dataset.row_count) * 100))

                    log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

                    return

            i += 1

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        self.task_update(task_status, '100% complete')

        log.info('Finished reindex, dataset_slug: %s' % dataset_slug)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from panda.models import Dataset

        dataset = Dataset.objects.get(slug=args[0])

        try:
            try:
                self.send_notifications(dataset, retval, einfo)
            finally:
                # If reindex failed, clear any data that might be staged
                if dataset.current_task.status == 'FAILURE':
                    solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % args[0], commit=True)
        finally:
            dataset.unlock()

    def send_notifications(self, dataset, retval, einfo):
        """
        Send user notifications this task has finished.
        """
        from panda.models import Notification

        task_status = dataset.current_task 

        if einfo:
            self.task_exception(
                task_status,
                'Reindex failed',
                u'\n'.join([einfo.traceback, unicode(retval)])
            )
            
            email_subject = 'Reindex failed: %s' % dataset.name
            email_message = 'Reindex failed: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Reindex failed: <strong>%s</strong>' % dataset.name
            notification_type = 'Error'
        elif self.is_aborted():
            email_subject = 'Reindex aborted: %s' % dataset.name
            email_message = 'Reindex aborted: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Reindex aborted: <strong>%s</strong>' % dataset.name
            notification_type = 'Info'
        else:
            self.task_complete(task_status, 'Reindex complete')
            
            email_subject = 'Reindex complete: %s' % dataset.name
            email_message = 'Reindex complete: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Reindex complete: <strong>%s</strong>' % dataset.name
            notification_type = 'Info'
        
        if task_status.creator:
            Notification.objects.create(
                recipient=task_status.creator,
                related_task=task_status,
                related_dataset=dataset,
                message=notification_message,
                type=notification_type
            )

            send_mail(email_subject, email_message, [task_status.creator.username])

