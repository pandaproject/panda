#!/usr/bin/env python

import datetime
import logging
from math import floor
import os.path
import time

from csvkit import CSVKitWriter
from django.conf import settings
from django.utils import simplejson as json
from livesettings import config_value

from panda import solr
from panda.tasks.export_file import ExportFileTask 

SOLR_PAGE_SIZE = 500

class ExportCSVTask(ExportFileTask):
    """
    Task to export all data for a dataset to a CSV.
    """
    name = 'panda.tasks.export.csv'

    def run(self, dataset_slug, query=None, filename=None, *args, **kwargs):
        """
        Execute export.
        """
        from panda.models import Dataset

        log = logging.getLogger(self.name)
        log.info('Beginning export, dataset_slug:%s %s' % (dataset_slug, query))

        try:
            dataset = Dataset.objects.get(slug=dataset_slug)
        except Dataset.DoesNotExist:
            log.warning('Export failed due to Dataset being deleted, dataset_slug: %s' % dataset_slug)

            return

        task_status = dataset.current_task
        task_status.begin('Preparing to export')

        if not filename:
            filename = '%s_%s.csv' % (dataset_slug, datetime.datetime.utcnow().isoformat())
        else:
            filename = '%s.csv' % filename

        path = os.path.join(settings.EXPORT_ROOT, filename)

        try:
            os.makedirs(os.path.realpath(os.path.dirname(path)))
        except:
            pass

        f = open(path, 'w')
        writer = CSVKitWriter(f)

        # Header
        writer.writerow([c['name'] for c in dataset.column_schema])

        solr_query = 'dataset_slug:%s' % dataset_slug

        if query:
            solr_query = '%s %s' % (solr_query, query)

        response = solr.query(
            settings.SOLR_DATA_CORE,
            solr_query,
            offset=0,
            limit=0
        )

        total_count = response['response']['numFound']
        n = 0
        throttle = config_value('PERF', 'TASK_THROTTLE')

        while n < total_count:
            response = solr.query(
                settings.SOLR_DATA_CORE,
                solr_query,
                offset=n,
                limit=SOLR_PAGE_SIZE
            )

            results = response['response']['docs']

            for row in results:
                data = json.loads(row['data'])

                writer.writerow(data)

            task_status.update('%.0f%% complete' % floor(float(n) / float(total_count) * 100))

            if self.is_aborted():
                task_status.abort('Aborted after exporting %.0f%%' % floor(float(n) / float(total_count) * 100))

                log.warning('Export aborted, dataset_slug: %s' % dataset_slug)

                return

            n += SOLR_PAGE_SIZE
            
            time.sleep(throttle)

        f.close()

        task_status.update('100% complete')

        log.info('Finished export, dataset_slug:%s %s' % (dataset_slug, query))

        return filename

