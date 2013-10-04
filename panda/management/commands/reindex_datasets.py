#!/usr/bin/env python

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from panda.models import Dataset

class Command(NoArgsCommand):
    help = _('Reindex all datasets')

    def handle_noargs(self, **options):
        for dataset in Dataset.objects.all():
            dataset.update_full_text()
            self.stdout.write(_('Updated: %s\n') % dataset.name)
        
        self.stdout.write(_('Done!\n'))

