#!/usr/bin/env python

from django.conf import settings

import csvdata as csv
import solr
import xls
import xlsx

def sniff_dialect(data_type, path):
    return globals()[data_type].sniff_dialect(path) 

def infer_schema(data_type, path, dialect, sample_size=settings.PANDA_SCHEMA_SAMPLE_ROWS):
    return globals()[data_type].infer_schema(path, dialect, sample_size) 

def sample_data(data_type, path, dialect, sample_size=settings.PANDA_SAMPLE_DATA_ROWS):
    return globals()[data_type].sample_data(path, dialect, sample_size) 

