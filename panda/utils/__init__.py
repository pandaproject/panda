#!/usr/bin/env python


from django.conf import settings

import column_schema
import csvdata as csv
import email
import passwords
import solr
import typecoercion
import xls
import xlsx

def sniff_dialect(data_type, path, encoding='utf-8'):
    return globals()[data_type].sniff_dialect(path, encoding=encoding) 

def extract_column_names(data_type, path, dialect, encoding='utf-8'):
    return globals()[data_type].extract_column_names(path, dialect, encoding=encoding) 

def sample_data(data_type, path, dialect, sample_size=settings.PANDA_SAMPLE_DATA_ROWS, encoding='utf-8'):
    return globals()[data_type].sample_data(path, dialect, sample_size, encoding=encoding) 

def guess_column_types(data_type, path, dialect, sample_size=settings.PANDA_SAMPLE_DATA_ROWS, encoding='utf-8'):
    return globals()[data_type].guess_column_types(path, dialect, sample_size, encoding=encoding) 

