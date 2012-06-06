#!/usr/bin/env python

import os.path
import traceback

from celery.contrib.abortable import AbortableTask
from django.conf import settings

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

        export = None
        extra_context = {
            'query': query,
            'related_dataset': dataset
        }
        url = None

        if einfo:
            if hasattr(einfo, 'traceback'):
                tb = einfo.traceback
            else:
                tb = ''.join(traceback.format_tb(einfo[2]))

            task_status.exception(
                'Export failed',
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )

            template_prefix = 'export_failed'
            extra_context['error'] = unicode(retval)
            extra_context['traceback'] = tb
            notification_type = 'Error'
        elif self.is_aborted():
            template_prefix = 'export_aborted'
            notification_type = 'Info'
        else:
            task_status.complete('Export complete')

            export = Export.objects.create(
                filename=retval,
                original_filename=retval,
                size=os.path.getsize(os.path.join(settings.EXPORT_ROOT, retval)),
                creator=task_status.creator,
                creation_date=task_status.start,
                dataset=dataset)

            url = '#export/%i' % export.id

            template_prefix = 'export_complete'
            notification_type = 'Info'
            
        if task_status.creator:
            notify(
                task_status.creator,
                template_prefix,
                notification_type,
                url,
                extra_context=extra_context
            )

