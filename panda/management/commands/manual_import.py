#!/usr/bin/env python

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from livesettings import config_value

from panda.models import Dataset, DataUpload, UserProxy

class Command(BaseCommand):
    args = '<dataset_filename user_email>'
    help = _('Manually import data for when the web UI fails. See http://panda.readthedocs.org/en/latest/manual_imports.html')

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stderr.write(_('You must specify a filename and user.\n'))
            return

        filename = args[0]
        email = args[1]

        path = os.path.join(settings.MEDIA_ROOT, filename)

        if not os.path.exists(path):
            self.stderr.write(_('File does not exist!\n'))
            return

        size = os.path.getsize(path)

        try:
            creator = UserProxy.objects.get(email=email)
        except UserProxy.DoesNotExist:
            self.stderr.write(_('User does not exist!\n'))
            return

        upload = DataUpload.objects.create(
            filename=filename,
            original_filename=filename,
            size=size,
            creator=creator,
            dataset=None,
            encoding='utf-8')
     
        dataset = Dataset.objects.create(
            name=filename,
            creator=creator,
            initial_upload=upload)

        self.stdout.write(_('Dataset created: http://%s/#dataset/%s\n') % (config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug))

        dataset.import_data(creator, upload)
        
        dataset.update_full_text()

        self.stdout.write(_('Import started. Check dataset page for progress.'))
