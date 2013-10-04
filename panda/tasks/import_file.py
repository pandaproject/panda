#!/usr/bin/env python

import logging
import traceback

from celery.contrib.abortable import AbortableTask
from django.conf import settings
from django.utils.translation import ugettext

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

        log = logging.getLogger(self.name)

        try:
            dataset = Dataset.objects.get(slug=args[0])
        except Dataset.DoesNotExist:
            log.warning('Can not send import notifications due to Dataset being deleted, dataset_slug: %s' % args[0])

            return

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

        extra_context = {
            'related_dataset': dataset
        }

        if einfo:
            if hasattr(einfo, 'traceback'):
                tb = einfo.traceback
            else:
                tb = ''.join(traceback.format_tb(einfo[2]))

            task_status.exception(
                ugettext('Import failed'),
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
            task_status.complete(ugettext('Import complete'))

            template_prefix = 'import_complete'
            extra_context['type_summary'] = retval.summarize()
            notification_type = 'Info'
        
        if task_status.creator:
            notify(
                task_status.creator,
                template_prefix,
                notification_type,
                url='#dataset/%s' % dataset.slug,
                extra_context=extra_context
            )

