#!/usr/bin/env python

from itertools import islice
from uuid import uuid4

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect
from csvkit.typeinference import normalize_table
from django.conf import settings
from django.utils import simplejson as json
import xlrd

def csv_sniff(f):
    return sniff_dialect(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))

def csv_infer_schema(f, dialect, sample_size=100):
    reader = CSVKitReader(f, **dialect)
    headers = reader.next()

    sample = islice(reader, sample_size)
    normal_types, normal_values = normalize_table(sample)
    type_names = [t.__name__ for t in normal_types]

    return [{
        'column': h,
        'type': t
    } for h, t in zip(headers, type_names)]

def xls_infer_schema(f, sample_size=100):
    book = xlrd.open_workbook(file_contents=f.read())
    sheet = book.sheet_by_index(0)

    headers = sheet.row_values(0)

    # TODO - actually figure out types

    return [{
        'column': h,
        'type': 'unicode'
    } for h in headers]

def csv_sample_data(f, dialect, sample_size=settings.PANDA_SAMPLE_DATA_ROWS):
    reader = CSVKitReader(f, **dialect)
    headers = reader.next()
        
    samples = []

    for row in islice(reader, sample_size):
        samples.append(row)

    return samples 

def xls_sample_data(f, sample_size=settings.PANDA_SAMPLE_DATA_ROWS):
    book = xlrd.open_workbook(file_contents=f.read())
    sheet = book.sheet_by_index(0)

    samples = []

    for i in range(1, min(sheet.nrows, sample_size)):
        values = sheet.row_values(i)

        samples.append(values)

    return samples

def make_solr_row(dataset, data, external_id=None):
    solr_row = {
        'dataset_slug': dataset.slug,
        'full_text': '\n'.join([unicode(d) for d in data]),
        'data': json.dumps(data)
    }

    if external_id:
        solr_row['id'] = '%s-%s' % (dataset.slug, external_id)
        solr_row['external_id'] = external_id
    else:
        solr_row['id'] = unicode(uuid4())

    return solr_row

