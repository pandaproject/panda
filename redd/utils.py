#!/usr/bin/env python

import datetime
from itertools import islice
from uuid import uuid4

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect
from csvkit.typeinference import normalize_table, NULL_TIME
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
    reader.next() # skip headers
        
    samples = []

    for row in islice(reader, sample_size):
        samples.append(row)

    return samples 

def xls_normalize_date(v, datemode):
    """
    Convert an xldate to a date, time, or datetime
    depending on its value.
    """
    v_tuple = xlrd.xldate_as_tuple(v, datemode)

    if v_tuple == (0, 0, 0, 0, 0, 0):
        # Midnight 
        return datetime.time(*v_tuple[3:]).isoformat()
    elif v_tuple[3:] == (0, 0, 0):
        # Date only
        return datetime.date(*v_tuple[:3]).isoformat()
    elif v_tuple[:3] == (0, 0, 0):
        # Time only
        return datetime.time(*v_tuple[3:]).isoformat()
    else:
        # Date and time
        return datetime.datetime(*v_tuple).isoformat()

def xlsx_normalize_date(dt):
    if dt.time() == NULL_TIME:
        return dt.date().isoformat()

    if dt.microsecond == 0:
        return dt.isoformat()

    ms = dt.microsecond

    if ms < 1000:
        return dt.replace(microsecond=0).isoformat()
    elif ms > 999000:
        return dt.replace(second=dt.second + 1, microsecond=0).isoformat()

    return dt.isoformat()

def xls_sample_data(f, sample_size=settings.PANDA_SAMPLE_DATA_ROWS):
    book = xlrd.open_workbook(file_contents=f.read(), on_demand=True)
    sheet = book.sheet_by_index(0)

    samples = []

    for i in range(1, min(sheet.nrows, sample_size)):
        values = sheet.row_values(i)
        types = sheet.row_types(i)

        values = [xls_normalize_date(v, book.datemode) if t == xlrd.biffh.XL_CELL_DATE else v for v, t in zip(values, types)]

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

