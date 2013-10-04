#!/usr/bin/env python

from itertools import chain
import logging
import os

from panda.tasks.base import Task
from django.conf import settings

SOLR_ADD_BUFFER_SIZE = 500

class PurgeOrphanedUploadsTask(Task):
    """
    Task to import all data for a dataset from a CSV.
    """
    name = 'panda.tasks.cron.purge_orphaned_uploads'

    def run(self, fake=False, *args, **kwargs):
        """
        Execute import.
        """
        from panda.models import DataUpload, RelatedUpload

        log = logging.getLogger(self.name)
        log.info('Purging orphaned uploads')

        local_files = os.listdir(settings.MEDIA_ROOT)
        data_uploads = DataUpload.objects.all()
        related_uploads = RelatedUpload.objects.all()

        for upload in chain(data_uploads, related_uploads):
            # This file is accounted for
            try:
                local_files.remove(upload.filename)
            except ValueError:
                pass

            if not upload.dataset:
                if fake:
                    log.info('Would delete upload: %s\n' % upload)
                else:
                    log.info('Deleted upload: %s\n' % upload)
                    upload.delete()

        for f in local_files:
            path = os.path.join(settings.MEDIA_ROOT, f)

            if fake:
                log.info('Would delete file: %s\n' % path)
            else:
                log.info('Deleted file: %s\n' % path)
                os.remove(path)

        log.info('Purge complete')

