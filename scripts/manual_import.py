#!/usr/bin/env python

"""
Script to import data when the web UI fails. See documentation at:

http://panda.readthedocs.org/en/latest/manual_imports.html

Dataset name, description, etc. are set to defaults. Change them in the web UI.
"""

import os
import sys

from django.core.management import setup_environ
from config.deployed import settings
setup_environ(settings)

from panda.models import Dataset, DataUpload, UserProxy

def main():
    filename = sys.argv[1]
    email = sys.argv[2]

    path = os.path.join(settings.MEDIA_ROOT, filename)
    size = os.path.getsize(path)
    creator = UserProxy.objects.get(email=email)

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

    dataset.import_data(creator, upload)
    
    dataset.update_full_text()

if __name__ == '__main__':
    main()

