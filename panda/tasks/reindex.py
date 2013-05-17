#!/usr/bin/env python

import logging
from math import floor
import time
import traceback

from panda.tasks.base import AbortableTask
from django.conf import settings
from django.utils import simplejson as json
from django.utils.translation import ugettext
from livesettings import config_value

from panda import solr, utils
from panda.utils.notifications import notify
from panda.utils.typecoercion import DataTyper 

SOLR_READ_BUFFER_SIZE = 500
SOLR_ADD_BUFFER_SIZE = 500

class ReindexTask(AbortableTask):
    """
    Task to import all data for a dataset from a CSV.
    """
    name = 'panda.tasks.reindex'

    def run(self, dataset_slug, *args, **kwargs):
        """
        Execute reindex.
        """
        from panda.models import Dataset
        
        log = logging.getLogger(self.name)
        log.info('Beginning reindex, dataset_slug: %s' % dataset_slug)

        try:
            dataset = Dataset.objects.get(slug=dataset_slug)
        except Dataset.DoesNotExist:
            log.warning('Reindexing failed due to Dataset being deleted, dataset_slug: %s' % dataset_slug)

            return

        task_status = dataset.current_task
        task_status.begin(ugettext('Preparing to reindex'))

        if self.is_aborted():
            task_status.abort(ugettext('Aborted during preparation'))

            log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

            return

        read_buffer = []
        add_buffer = []
        data_typer = DataTyper(dataset.column_schema)
        throttle = config_value('PERF', 'TASK_THROTTLE')

        i = 0

        while i < dataset.row_count:
            if not read_buffer:
                query = 'dataset_slug: %s' % (dataset.slug)
                response = solr.query(settings.SOLR_DATA_CORE, query, limit=SOLR_READ_BUFFER_SIZE, offset=i)
                read_buffer = response['response']['docs']

            data = read_buffer.pop(0)
            row = json.loads(data['data'])

            new_data = utils.solr.make_data_row(dataset, row)
            new_data['id'] = data['id'] 
            new_data['data_upload_id'] = data['data_upload_id']
            new_data = data_typer(new_data, row)

            add_buffer.append(new_data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(settings.SOLR_DATA_CORE, add_buffer)

                add_buffer = []

                task_status.update(ugettext('%.0f%% complete') % floor(float(i) / float(dataset.row_count) * 100))

                if self.is_aborted():
                    task_status.abort(ugettext('Aborted after reindexing %.0f%%') % floor(float(i) / float(dataset.row_count) * 100))

                    log.warning('Reindex aborted, dataset_slug: %s' % dataset_slug)

                    return
            
                time.sleep(throttle)

            i += 1

        if add_buffer:
            solr.add(settings.SOLR_DATA_CORE, add_buffer)
            add_buffer = []

        solr.commit(settings.SOLR_DATA_CORE)

        task_status.update(ugettext('100% complete'))

        # Refresh dataset
        try:
            dataset = Dataset.objects.get(slug=dataset_slug)
        except Dataset.DoesNotExist:
            log.warning('Reindexing could not be completed due to Dataset being deleted, dataset_slug: %s' % dataset_slug)

            return

        dataset.column_schema = data_typer.schema 
        dataset.save()

        log.info('Finished reindex, dataset_slug: %s' % dataset_slug)

        return data_typer

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from panda.models import Dataset

        log = logging.getLogger(self.name)

        try:
            dataset = Dataset.objects.get(slug=args[0])
        except Dataset.DoesNotExist:
            log.warning('Can not send reindexing notifications due to Dataset being deleted, dataset_slug: %s' % args[0])

            return

        try:
            try:
                self.send_notifications(dataset, retval, einfo)
            finally:
                # If reindex failed, clear any data that might be staged
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
                ugettext('Reindex failed'),
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )
            
            template_prefix = 'reindex_failed'
            notification_type = 'Error'
        elif self.is_aborted():
            template_prefix = 'reindex_aborted'
            notification_type = 'Info'
        else:
            task_status.complete(ugettext('Reindex complete'))

            template_prefix = 'reindex_complete'
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

