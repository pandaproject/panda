#!/usr/bin/env python

from datetime import datetime

from celery.contrib.abortable import AbortableTask
from django.conf import settings

from redd import solr

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
        task_status.start = datetime.now()
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
        task_status.end = datetime.now()
        task_status.message = message
        task_status.save()

    def task_complete(self, task_status, message):
        """
        Mark that task has completed.
        """
        task_status.status = 'SUCCESS'
        task_status.end = datetime.now()
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

    def run(self, dataset_slug, *args, **kwargs):
        """
        Execute export.
        """
        raise NotImplementedError() 

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from redd.models import Dataset, Notification

        dataset = Dataset.objects.get(slug=args[0])
        task_status = dataset.current_task 

        notification = Notification(
            recipient=dataset.creator,
            related_task=task_status,
            related_dataset=dataset
        )

        if einfo:
            self.task_exception(
                task_status,
                'Export failed',
                u'\n'.join([einfo.traceback, unicode(retval)])
            )
            
            notification.message = 'Export of %s failed' % dataset.name
            notification.type = 'error'
        else:
            self.task_complete(task_status, 'Export complete')
            
            notification.message = 'Export of <strong>%s</strong> complete' % dataset.name
        
        notification.save()

