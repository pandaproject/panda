#!/usr/bin/env python

from datetime import datetime
import os.path

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from livesettings import config_value

from redd.utils.mail import send_mail

class ExportFileTask(AbortableTask):
    """
    Base type for file export tasks. 
    """
    abstract = True

    # All subclasses should be within this namespace
    name = 'redd.tasks.export'

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

    def run(self, dataset_slug, *args, **kwargs):
        """
        Execute export.
        """
        raise NotImplementedError() 

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import Dataset, Export, Notification

        dataset = Dataset.objects.get(slug=args[0])
        task_status = dataset.current_task

        if einfo:
            error_detail = u'\n'.join([einfo.traceback, unicode(retval)])

            self.task_exception(
                task_status,
                'Export failed',
                error_detail)
            
            email_subject = 'Export failed: %s' % dataset.name
            email_message = 'Export failed: %s:\n%s' % (dataset.name, error_detail)
            notification_message = 'Export failed: <strong>%s</strong>' % dataset.name
            notification_type = 'Error'
        else:
            self.task_complete(task_status, 'Export complete')
            
            export = Export.objects.create(
                filename=retval,
                original_filename=retval,
                size=os.path.getsize(os.path.join(settings.EXPORT_ROOT, retval)),
                creator=task_status.creator,
                creation_date=task_status.start,
                dataset=dataset)
            
            email_subject = 'Export complete: %s' % dataset.name
            email_message = 'Export complete: %s. Download your results:\n\nhttp://%s/api/1.0/export/%i/download/' % (dataset.name, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
            notification_message = 'Export complete: <strong>%s</strong>' % dataset.name
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

