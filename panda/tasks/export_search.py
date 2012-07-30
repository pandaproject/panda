#!/usr/bin/env python

import logging
from math import floor
import os.path
import time
from traceback import format_tb
from zipfile import ZipFile

from celery.contrib.abortable import AbortableTask
from csvkit import CSVKitWriter
from django.conf import settings
from django.utils import simplejson as json
from django.utils.timezone import now 
from livesettings import config_value

from panda import solr
from panda.utils.notifications import notify

SOLR_PAGE_SIZE = 500

class ExportSearchTask(AbortableTask):
    """
    Task to export all search results to a batch of CSV files.
    """
    name = 'panda.tasks.export.search'

    def run(self, query, task_status_id, filename=None, *args, **kwargs):
        """
        Execute export.
        """
        from panda.models import Dataset, TaskStatus

        log = logging.getLogger(self.name)
        log.info('Beginning export, query: %s' % query)

        task_status = TaskStatus.objects.get(id=task_status_id)
        task_status.begin('Preparing to import')

        if not filename:
            filename = 'search_export_%s' % (now().isoformat())

        zip_name = '%s.zip' % filename

        path = os.path.join(settings.EXPORT_ROOT, filename)
        zip_path = os.path.join(settings.EXPORT_ROOT, zip_name)
        
        zipfile = ZipFile(zip_path, 'w')

        try:
            os.makedirs(os.path.realpath(path))
        except:
            pass

        response = solr.query_grouped(
            settings.SOLR_DATA_CORE,
            query,
            'dataset_slug',
            offset=0,
            limit=1000,
            group_limit=0,
            group_offset=0
        )
        groups = response['grouped']['dataset_slug']['groups']

        datasets = {}

        for group in groups:
            dataset_slug = group['groupValue']
            count = group['doclist']['numFound']

            datasets[dataset_slug] = count

        total_n = 0
        throttle = config_value('PERF', 'TASK_THROTTLE')

        for dataset_slug in datasets:
            try:
                dataset = Dataset.objects.get(slug=dataset_slug)
            except Dataset.DoesNotExist:
                log.warning('Skipping part of export due to Dataset being deleted, dataset_slug: %s' % dataset_slug)

                continue

            filename = '%s.csv' % dataset_slug
            file_path = os.path.join(path, filename)

            f = open(file_path, 'w')
            writer = CSVKitWriter(f)
            
            # Header
            writer.writerow([c['name'] for c in dataset.column_schema])
                
            response = solr.query(
                settings.SOLR_DATA_CORE,
                query,
                offset=0,
                limit=0
            )

            # Update dataset and total counts for progress tracking
            datasets[dataset_slug] = response['response']['numFound']
            total_count = sum(datasets.values())

            n = 0

            while n < datasets[dataset_slug]:
                response = solr.query(
                    settings.SOLR_DATA_CORE,
                    'dataset_slug: %s %s' % (dataset_slug, query),
                    offset=n,
                    limit=SOLR_PAGE_SIZE
                )

                results = response['response']['docs']

                for row in results:
                    data = json.loads(row['data'])

                    writer.writerow(data)

                task_status.update('%.0f%% complete' % floor(float(total_n) / float(total_count) * 100))

                if self.is_aborted():
                    task_status.abort('Aborted after exporting %.0f%%' % floor(float(total_n) / float(total_count) * 100))

                    log.warning('Export aborted, query: %s' % query)

                    return

                n += SOLR_PAGE_SIZE
                total_n += response['response']['numFound'] 
                
                time.sleep(throttle)

            f.close()

            # Add to zip and nuke temp file
            zipfile.write(file_path, filename)
            os.remove(file_path)

        # Finish zip file and nuke temp directory
        zipfile.close()
        os.rmdir(path)

        task_status.update('100% complete')

        log.info('Finished export, query: %s' % query)

        return zip_name

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Save final status, results, etc.
        """
        from panda.models import TaskStatus

        query = args[0]
        task_status = TaskStatus.objects.get(id=args[1])

        self.send_notifications(query, task_status, retval, einfo) 

    def send_notifications(self, query, task_status, retval, einfo):
        """
        Send user notifications this task has finished.
        """
        from panda.models import Export

        export = None
        extra_context = { 'query': query }
        url = None

        if einfo:
            if isinstance(einfo, tuple):
                tb = '\n'.join(format_tb(einfo[2]))
            else:
                tb = einfo.traceback

            task_status.exception(
                'Export failed',
                u'%s\n\nTraceback:\n%s' % (unicode(retval), tb)
            )
            
            template_prefix = 'export_search_failed'
            extra_context['error'] = unicode(retval)
            extra_context['traceback'] = tb
            notification_type = 'Error'
        elif self.is_aborted():
            template_prefix = 'export_search_aborted'
            notification_type = 'Info'
        else:
            task_status.complete('Export complete')

            export = Export.objects.create(
                filename=retval,
                original_filename=retval,
                size=os.path.getsize(os.path.join(settings.EXPORT_ROOT, retval)),
                creator=task_status.creator,
                creation_date=task_status.start,
                dataset=None)

            url = '#export/%i' % export.id

            template_prefix = 'export_search_complete'
            notification_type = 'Info'

        if task_status.creator:
            notify(
                task_status.creator,
                template_prefix,
                notification_type,
                url,
                extra_context=extra_context
            )

