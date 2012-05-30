#!/usr/bin/env python

import traceback

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from livesettings import config_value

from panda import solr
from panda.utils.notifications import notify

SOLR_ADD_BUFFER_SIZE = 500

class ImportFileTask(AbortableTask):
    """
    Base type for file import tasks. 
    """
    abstract = True

    # All subclasses should be within this namespace
    name = 'panda.tasks.import'

    def run(self, dataset_slug, upload_id, *args, **kwargs):
        """
        Execute import.
        """
        raise NotImplementedError() 

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
                # If import failed, clear any data that might be staged
                if dataset.current_task.status == 'FAILURE':
                    solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % args[0], commit=True)
        finally:
            dataset.unlock()

    def send_notifications(self, dataset, retval, einfo):
        """
        Send user notifications this task has finished.
        """
        task_status = dataset.current_task 

        if einfo:
            if hasattr(einfo, 'traceback'):
                tb = einfo.traceback
            else:
                tb = ''.join(traceback.format_tb(einfo[2]))

            task_status.exception(
                'Import failed',
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )
            
            email_subject = 'Import failed: %s' % dataset.name
            email_message = 'Import failed: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Import failed: <strong>%s</strong>' % dataset.name
            notification_type = 'Error'
        elif self.is_aborted():
            email_subject = 'Import aborted: %s' % dataset.name
            email_message = 'Import aborted: %s:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Import aborted: <strong>%s</strong>' % dataset.name
            notification_type = 'Info'
        else:
            task_status.complete('Import complete')
            
            email_subject = 'Import complete: %s' % dataset.name
            email_message = 'Import complete: %s (%i rows)\n\nhttp://%s/#dataset/%s' % (dataset.name, dataset.row_count or 0, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)

            type_summary = retval.summarize()

            if type_summary:
                email_message += '\n\n' + type_summary

            notification_message = 'Import complete: <strong>%s</strong>' % dataset.name
            notification_type = 'Info'
        
        if task_status.creator:
            notify(
                task_status.creator,
                notification_message,
                notification_type,
                related_task=task_status,
                related_dataset=dataset,
                related_export=None,
                email_subject=email_subject,
                email_message=email_message
            )

