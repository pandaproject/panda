#!/usr/bin/env python

import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from livesettings import config_value

from optparse import make_option
from panda.models import Dataset, DataUpload, UserProxy
from panda.utils.typecoercion import TYPE_NAMES_MAPPING

class Command(BaseCommand):
    args = '<dataset_filename user_email>'
    help = _('Manually import data for when the web UI fails. See http://panda.readthedocs.org/en/latest/manual_imports.html')

    option_list = BaseCommand.option_list + (
        make_option('-o', '--schema_overrides',
            action='store',
            dest='overrides',
            help=_('Full path to CSV containing schema overrides. Field types: %s' % ', '.join(sorted(TYPE_NAMES_MAPPING.keys())))
        ),
    )

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stderr.write(_('You must specify a filename and user.\n'))
            return

        filename = args[0]
        email = args[1]
        overrides = self._schema_overrides(options)

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

        self.stdout.write('%s http://%s/#dataset/%s\n' % (_('Dataset created:'), config_value('DOMAIN', 'SITE_DOMAIN'), dataset.slug))

        dataset.import_data(creator, upload, schema_overrides=overrides)

        dataset.update_full_text()

        self.stdout.write(_('Import started. Check dataset page for progress.\n'))

    def _schema_overrides(self, opts):
        try:
            fields_file = opts['overrides']
        except KeyError:
            return {}
        #TODO: error-handling if file doesn't exist or is malformed
        valid_types = set(TYPE_NAMES_MAPPING.keys())
        with open(fields_file) as csvfile:
            data = {}
            for field, dtype in csv.reader(csvfile):
                # Activate indexing
                data[field] = { 'indexed': True }
                # Update data type if provided and valid
                if dtype in valid_types:
                    data[field]['type'] =  dtype
        return data
