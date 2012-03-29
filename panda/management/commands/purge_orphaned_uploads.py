#!/usr/bin/env python

from itertools import chain
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from panda.models import DataUpload, RelatedUpload

class Command(BaseCommand):
    help = 'Audit uploads and local files; delete any not associated with a dataset'

    def handle(self, *args, **options):
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
                self.stdout.write('Deleted upload: %s\n' % upload)
                upload.delete()

        for f in local_files:
            path = os.path.join(settings.MEDIA_ROOT, f)
            self.stdout.write('Deleted file: %s\n' % path)
            os.remove(path)

