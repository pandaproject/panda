#!/usr/bin/env python

from itertools import chain
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from optparse import make_option
from panda.models import DataUpload, RelatedUpload

class Command(BaseCommand):
    help = 'Audit uploads and local files, deleting any not associated with a dataset.'
    option_list = BaseCommand.option_list + (
        make_option('--fake',
            action='store_true',
            dest='fake',
            default=False,
            help='Only describe what files would be deleted, don\'t actually delete them.'),
        )

    def handle(self, *args, **options):
        if options['fake']:
            self.stdout.write('Running in fake mode! No files will actually be deleted!')

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
                if options['fake']:
                    self.stdout.write('Would delete upload: %s\n' % upload)
                else:
                    self.stdout.write('Deleted upload: %s\n' % upload)
                    upload.delete()

        for f in local_files:
            path = os.path.join(settings.MEDIA_ROOT, f)

            if options['fake']:
                self.stdout.write('Would delete file: %s\n' % path)
            else:
                self.stdout.write('Deleted file: %s\n' % path)
                os.remove(path)

