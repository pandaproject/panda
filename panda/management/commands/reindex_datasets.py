#!/usr/bin/env python

from django.core.management.base import NoArgsCommand

from panda.models import Dataset

class Command(NoArgsCommand):
    help = 'Reindex all datasets'

    def handle_noargs(self, **options):
        for dataset in Dataset.objects.all():
            dataset.update_full_text()
            self.stdout.write('Updated: %s\n' % dataset.name)
        
        self.stdout.write('Done!\n')

