#!/usr/bin/env python

import os.path
import traceback
from urllib import unquote

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from livesettings import config_value

from panda.utils.notifications import notify

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
        from panda.models import Export

        task_status = dataset.current_task 
        dataset_name = unquote(dataset.name)

        if einfo:
            if hasattr(einfo, 'traceback'):
                tb = einfo.traceback
            else:
                tb = ''.join(traceback.format_tb(einfo[2]))

            error_detail = u'\n'.join([tb, unicode(retval)])

            task_status.exception(
                'Export failed',
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )
            
            if query:
                email_subject = 'Export failed: "%s" in %s' % (query, dataset_name)
                email_message = 'Export failed: "%s" in %s\n%s' % (query, dataset_name, error_detail)
                notification_message = 'Export failed: <strong>"%s" in %s</strong>' % (query, dataset_name)
            else:
                email_subject = 'Export failed: %s' % dataset_name
                email_message = 'Export failed: %s\n%s' % (dataset_name, error_detail)
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
                email_message = 'Export complete: "%s" in %s. Download your results:\n\nhttp://%s/#export/%i' % (query, dataset_name, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
                notification_message = 'Export complete: <strong>"%s" in %s</strong>' % (query, dataset_name)
            else:
                email_subject = 'Export complete: %s' % dataset_name
                email_message = 'Export complete: %s. Download your results:\n\nhttp://%s/#export/%i' % (dataset_name, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
                notification_message = 'Export complete: <strong>%s</strong>' % dataset_name

            notification_type = 'Info'

        if task_status.creator:
            notify(
                task_status.creator,
                notification_message,
                notification_type,
                related_task=task_status,
                related_dataset=dataset,
                related_export=export,
                email_subject=email_subject,
                email_message=email_message
            )

