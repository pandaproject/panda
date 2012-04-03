#!/usr/bin/env python

import os.path

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from livesettings import config_value

from panda.utils.mail import send_mail

class ExportFileTask(AbortableTask):
    """
    Base type for file export tasks. 
    """
    abstract = True

    # All subclasses should be within this namespace
    name = 'panda.tasks.export'

    def run(self, dataset_slug, *args, **kwargs):
        """
        Execute export.
        """
        raise NotImplementedError() 

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from panda.models import Dataset

        dataset = Dataset.objects.get(slug=args[0])

        try:
            self.send_notifications(dataset, retval, einfo) 
        finally:
            dataset.unlock()

    def send_notifications(self, dataset, retval, einfo):
        """
        Send user notifications this task has finished.
        """
        from panda.models import Export, Notification

        task_status = dataset.current_task 

        if einfo:
            error_detail = u'\n'.join([einfo.traceback, unicode(retval)])

            task_status.exception('Export failed', error_detail)
            
            email_subject = 'Export failed: %s' % dataset.name
            email_message = 'Export failed: %s:\n%s' % (dataset.name, error_detail)
            notification_message = 'Export failed: <strong>%s</strong>' % dataset.name
            notification_type = 'Error'
        else:
            task_status.complete('Export complete')

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

