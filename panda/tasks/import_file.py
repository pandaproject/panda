#!/usr/bin/env python

import traceback

from celery.contrib.abortable import AbortableTask
from django.conf import settings

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

        extra_context = {}

        if einfo:
            if hasattr(einfo, 'traceback'):
                tb = einfo.traceback
            else:
                tb = ''.join(traceback.format_tb(einfo[2]))

            task_status.exception(
                'Import failed',
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )
            
            template_prefix = 'import_failed'
            extra_context['error'] = unicode(retval)
            extra_context['traceback'] = tb
            notification_type = 'Error'
        elif self.is_aborted():
            template_prefix = 'import_aborted'
            notification_type = 'Info'
        else:
            task_status.complete('Import complete')

            template_prefix = 'import_complete'
            extra_context['type_summary'] = retval.summarize()
            notification_type = 'Info'
        
        if task_status.creator:
            notify(
                task_status.creator,
                template_prefix,
                notification_type,
                related_task=task_status,
                related_dataset=dataset,
                related_export=None,
                extra_context=extra_context
            )

