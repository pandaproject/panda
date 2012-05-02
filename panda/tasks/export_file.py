#!/usr/bin/env python

import os.path
from urllib import unquote

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
        query = kwargs.get('query', None)

        try:
            self.send_notifications(dataset, query, retval, einfo) 
        finally:
            dataset.unlock()

    def send_notifications(self, dataset, query, retval, einfo):
        """
        Send user notifications this task has finished.
        """
        from panda.models import Export, Notification

        task_status = dataset.current_task 
        dataset_name = unquote(dataset.name)

        if einfo:
            error_detail = u'\n'.join([einfo.traceback, unicode(retval)])

            task_status.exception('Export failed', error_detail)
            
            if query:
                email_subject = 'Export failed: "%s" in %s' % (query, dataset_name)
                email_message = 'Export failed: "%s" in %s:\n%s' % (query, dataset_name, error_detail)
                notification_message = 'Export failed: <strong>"%s" in %s</strong>' % (query, dataset_name)
            else:
                email_subject = 'Export failed: %s' % dataset_name
                email_message = 'Export failed: %s:\n%s' % (dataset_name, error_detail)
                notification_message = 'Export failed: <strong>%s</strong>' % dataset_name

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
            
            if query:
                email_subject = 'Export complete: "%s" in %s' % (query, dataset_name)
                email_message = 'Export complete: "%s" in %s. Download your results:\n\nhttp://%s/api/1.0/export/%i/download/' % (query, dataset_name, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
                notification_message = 'Export complete: <strong>"%s" in %s</strong>' % (query, dataset_name)
            else:
                email_subject = 'Export complete: %s' % dataset_name
                email_message = 'Export complete: %s. Download your results:\n\nhttp://%s/api/1.0/export/%i/download/' % (dataset_name, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
                notification_message = 'Export complete: <strong>%s</strong>' % dataset_name

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

