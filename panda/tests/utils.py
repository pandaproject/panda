#!/usr/bin/env python

import os.path
from shutil import copyfile

from django.conf import settings
from livesettings import config_get

from panda import solr
from panda.models import Dataset, DataUpload, RelatedUpload, UserProxy

TEST_DATA_PATH = os.path.join(settings.SITE_ROOT, 'test_data')
TEST_DATA_FILENAME = 'contributors.csv'
TEST_XLS_FILENAME = 'contributors.xls'
TEST_CSV_TYPES_FILENAME = 'test_types.csv'
TEST_XLS_TYPES_FILENAME = 'test_types.xls'
TEST_XLSX_TYPES_FILENAME = 'test_types.xlsx'
TEST_EXCEL_XLSX_FILENAME = 'contributors.excel.xlsx'
TEST_OO_XLSX_FILENAME = 'contributors.oo.xlsx'
TEST_LATIN1_FILENAME = 'test_not_unicode_sample.csv'
TEST_LATIN1_DATA_FILENAME = 'test_not_unicode_data.csv'
TEST_MONEY = 'test_money.csv'

def setup_test_solr():
    settings.SOLR_DATA_CORE = 'data_test'
    settings.SOLR_DATASETS_CORE = 'datasets_test'
    config_get('PERF', 'TASK_THROTTLE').update(0.0) 
    solr.delete(settings.SOLR_DATA_CORE, '*:*')
    solr.delete(settings.SOLR_DATASETS_CORE, '*:*')

def get_auth_headers(email='user@pandaproject.net'):
    user = UserProxy.objects.get(email=email)

    return {
        'HTTP_PANDA_EMAIL': email,
        'HTTP_PANDA_API_KEY': user.api_key.key
    }

def get_admin_user():
    return UserProxy.objects.get(email='panda@pandaproject.net')

def get_panda_user():
    return UserProxy.objects.get(email='user@pandaproject.net')

def get_test_dataset(creator):
    dataset = Dataset.objects.create(
        name='Contributors',
        description='Biographic information about contributors to the PANDA project.',
        creator=creator)
    
    dataset.update_full_text()

    return dataset

def get_test_data_upload(creator, dataset, filename=TEST_DATA_FILENAME, encoding='utf8', size=None):
    # Ensure panda subdir has been created
    try:
        os.mkdir(settings.MEDIA_ROOT)
    except OSError:
        pass

    src = os.path.join(TEST_DATA_PATH, filename)
    dst = os.path.join(settings.MEDIA_ROOT, filename)
    copyfile(src, dst)

    return DataUpload.objects.create(
        filename=filename,
        original_filename=filename,
        size=size or os.path.getsize(dst),
        creator=creator,
        dataset=dataset,
        encoding=encoding)

def get_test_related_upload(creator, dataset, filename=TEST_DATA_FILENAME):
    # Ensure panda subdir has been created
    try:
        os.mkdir(settings.MEDIA_ROOT)
    except OSError:
        pass

    src = os.path.join(TEST_DATA_PATH, filename)
    dst = os.path.join(settings.MEDIA_ROOT, filename)
    copyfile(src, dst)

    return RelatedUpload.objects.create(
        filename=filename,
        original_filename=filename,
        size=os.path.getsize(dst),
        creator=creator,
        dataset=dataset)

