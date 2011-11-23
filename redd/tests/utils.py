#!/usr/bin/env python

import os.path
from shutil import copyfile
from time import sleep

from django.conf import settings
from django.contrib.auth.models import User

from redd import solr
from redd.models import Dataset, Upload

TEST_DATA_PATH = os.path.join(settings.SITE_ROOT, 'test_data')
TEST_DATA_FILENAME = 'contributors.csv'

def clear_solr():
    solr.delete('*:*', core=settings.SOLR_DATA_CORE)
    solr.delete('*:*', core=settings.SOLR_DATASETS_CORE)

def get_auth_headers(email='user@pandaproject.net'):
    user = User.objects.get(username=email)

    return {
        'HTTP_PANDA_EMAIL': email,
        'HTTP_PANDA_API_KEY': user.api_key.key
    }

def get_admin_user():
    return User.objects.get(username='panda@pandaproject.net')

def get_panda_user():
    return User.objects.get(username='user@pandaproject.net')

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

