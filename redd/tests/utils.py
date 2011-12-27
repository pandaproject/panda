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
TEST_XLS_FILENAME = 'contributors.xls'
TEST_EXCEL_XLSX_FILENAME = 'contributors.excel.xlsx'
TEST_OO_XLSX_FILENAME = 'contributors.oo.xlsx'

def setup_test_solr():
    settings.SOLR_DATA_CORE = 'data_test'
    settings.SOLR_DATASETS_CORE = 'datasets_test'
    solr.delete(settings.SOLR_DATA_CORE, '*:*')
    solr.delete(settings.SOLR_DATASETS_CORE, '*:*')

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

def get_test_upload(creator, filename=TEST_DATA_FILENAME):
    # Ensure panda subdir has been created
    try:
        os.mkdir(settings.MEDIA_ROOT)
    except OSError:
        pass

    src = os.path.join(TEST_DATA_PATH, filename)
    dst = os.path.join(settings.MEDIA_ROOT, filename)
    copyfile(src, dst)

    return Upload.objects.create(
        filename=filename,
        original_filename=filename,
        size=os.path.getsize(dst),
        creator=creator)

def get_test_dataset(upload, creator):
    return Dataset.objects.create(
        name='Contributors',
        description='Biographic information about contributors to the PANDA project.',
        data_upload=upload,
        creator=creator)

def wait():
    sleep(1)

