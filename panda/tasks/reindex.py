#!/usr/bin/env python

import logging
from math import floor
import time

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from django.utils import simplejson as json
from livesettings import config_value

from panda import solr, utils
from panda.utils.mail import send_mail
from panda.utils.typecoercion import DataTyper 

SOLR_READ_BUFFER_SIZE = 500
SOLR_ADD_BUFFER_SIZE = 500

class ReindexTask(AbortableTask):
    """
    Task to import all data for a dataset from a CSV.
    """
    name = 'panda.tasks.reindex'

    def run(self, dataset_slug, *args, **kwargs):
        """
        Execute reindex.
        """
        from panda.models import Dataset
        
        log = logging.getLogger(self.name)
        log.info('Beginning reindex, dataset_slug: %s' % dataset_slug)

        dataset = Dataset.objects.get(slug=dataset_slug)

        task_status = dataset.current_task
        task_status.begin('Preparing to reindex')

        if self.is_aborted():
            task_status.abort('Aborted during preperation')

            log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

            return

        read_buffer = []
        add_buffer = []
        data_typer = DataTyper(dataset.column_schema)
        throttle = config_value('MISC', 'TASK_THROTTLE')

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
            new_data = data_typer(new_data, row)

            add_buffer.append(new_data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)

                add_buffer = []

                task_status.update('%.0f%% complete' % floor(float(i) / float(dataset.row_count) * 100))

                if self.is_aborted():
                    task_status.abort('Aborted after reindexing %.0f%%' % floor(float(i) / float(dataset.row_count) * 100))

                    log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

                    return
            
                time.sleep(throttle)

            i += 1

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        task_status.update('100% complete')

        # Refresh dataset
        dataset = Dataset.objects.get(slug=dataset_slug)
        dataset.column_schema = data_typer.schema 
        dataset.save()

        log.info('Finished reindex, dataset_slug: %s' % dataset_slug)

        return data_typer

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
            task_status.exception(
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
            task_status.complete('Reindex complete')
            
            email_subject = 'Reindex complete: %s' % dataset.name
            email_message = 'Reindex complete: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)

            type_summary = retval.summarize()

            if type_summary:
                email_message += '\n\n' + type_summary

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

