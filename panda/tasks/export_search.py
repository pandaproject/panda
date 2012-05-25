#!/usr/bin/env python

import datetime
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
from livesettings import config_value

from panda import solr
from panda.utils.mail import send_mail

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
            filename = 'search_export_%s' % (datetime.datetime.utcnow().isoformat())

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
            dataset = Dataset.objects.get(slug=dataset_slug)

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
        from panda.models import Export, Notification

        if einfo:
            if isinstance(einfo, tuple):
                traceback = '\n'.join(format_tb(einfo[2]))
            else:
                traceback = einfo.traceback

            error_detail = u'\n'.join([traceback, unicode(retval)])

            task_status.exception('Export failed', error_detail)
            
            email_subject = 'Export failed: %s' % query
            email_message = 'Export failed: %s:\n%s' % (query, error_detail)
            notification_message = 'Export failed: <strong>%s</strong>' % (query)
            notification_type = 'Error'
        else:
            task_status.complete('Export complete')

            export = Export.objects.create(
                filename=retval,
                original_filename=retval,
                size=os.path.getsize(os.path.join(settings.EXPORT_ROOT, retval)),
                creator=task_status.creator,
                creation_date=task_status.start,
                dataset=None)
            
            email_subject = 'Export complete: %s' % query
            email_message = 'Export complete: %s. Download your results:\n\nhttp://%s/#export/%i' % (query, config_value('DOMAIN', 'SITE_DOMAIN', export.id), export.id)
            notification_message = 'Export complete: <strong>%s</strong>' % query
            notification_type = 'Info'

        if task_status.creator:
            Notification.objects.create(
                recipient=task_status.creator,
                related_task=task_status,
                related_dataset=None,
                related_export=export,
                message=notification_message,
                type=notification_type
            )
            
            send_mail(email_subject, email_message, [task_status.creator.username])

