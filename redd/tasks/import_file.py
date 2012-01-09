#!/usr/bin/env python

from datetime import datetime

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from livesettings import config_value

from redd import solr
from redd.utils.mail import send_mail

SOLR_ADD_BUFFER_SIZE = 500

class ImportFileTask(AbortableTask):
    """
    Base type for file import tasks. 
    """
    abstract = True

    # All subclasses should be within this namespace
    name = 'redd.tasks.import'

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
        task_status.message = message 
        task_status.traceback = formatted_traceback
        task_status.save()

    def run(self, dataset_slug, upload_id, *args, **kwargs):
        """
        Execute import.
        """
        raise NotImplementedError() 

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import Dataset, Notification

        dataset = Dataset.objects.get(slug=args[0])
        task_status = dataset.current_task 

        if einfo:
            self.task_exception(
                task_status,
                'Import failed',
                u'\n'.join([einfo.traceback, unicode(retval)])
            )
            
            email_message = 'Import of %s failed:\n%shttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Import of <strong>%s</strong> failed' % dataset.name
            notification_type = 'Error'
        else:
            self.task_complete(task_status, 'Import complete')
            
            email_message = 'Import of %s complete:\n\nhttp://%s/#dataset/%s' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug)
            notification_message = 'Import of <strong>%s</strong> complete' % dataset.name
            notification_type = 'Info'
        
        notification = Notification.objects.create(
            recipient=dataset.creator,
            related_task=task_status,
            related_dataset=dataset,
            message=notification_message,
            type=notification_type
        )

        send_mail(notification.type, email_message, [dataset.creator.username])

        # If import failed, clear any data that might be staged
        if task_status.status == 'FAILURE':
            solr.delete(settings.SOLR_DATA_CORE, 'dataset_slug:%s' % args[0], commit=True)

