#!/usr/bin/env python

import os.path
from shutil import copyfile
from time import sleep

from django.conf import settings
from django.contrib.auth.models import User
from sunburnt import SolrInterface

from redd.models import Dataset, Upload

TEST_DATA_PATH = os.path.join(settings.SITE_ROOT, 'test_data')
TEST_DATA_FILENAME = 'contributors.csv'

def get_test_solr():
    settings.SOLR_ENDPOINT = 'http://localhost:8983/solr/data_test'

    solr = SolrInterface(settings.SOLR_ENDPOINT) 
    solr.delete(queries='*:*', commit=True)

    return solr

def get_auth_headers():
    return {
        'HTTP_PANDA_EMAIL': 'panda@pandaproject.net',
        'HTTP_PANDA_API_KEY': User.objects.get(username='panda@pandaproject.net').api_key.key
    }

def get_test_user():
    return User.objects.get(username='panda@pandaproject.net')

def get_test_upload(creator):
    # Ensure panda subdir has been created
    try:
        os.mkdir(settings.MEDIA_ROOT)
    except OSError:
        pass

    src = os.path.join(TEST_DATA_PATH, TEST_DATA_FILENAME)
    dst = os.path.join(settings.MEDIA_ROOT, TEST_DATA_FILENAME)
    copyfile(src, dst)

    return Upload.objects.create(
        filename=TEST_DATA_FILENAME,
        original_filename=TEST_DATA_FILENAME,
        size=os.path.getsize(dst),
        creator=creator)

def get_test_dataset(upload, creator):
    return Dataset.objects.create(
        name='Contributors',
        description='Biographic information about contributors to the PANDA project.',
        data_upload=upload,
        creator=creator)        

def wait():
    sleep(3)

