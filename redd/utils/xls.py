#!/usr/bin/env python

import datetime

import xlrd

def sniff_dialect(path):
    return {} 

def infer_schema(path, dialect, sample_size):
    book = xlrd.open_workbook(path, on_demand=True)
    sheet = book.sheet_by_index(0)

    headers = sheet.row_values(0)

    # TODO - actually figure out types

    return [{
        'column': h,
        'type': 'unicode'
    } for h in headers]

def normalize_date(v, datemode):
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

def sample_data(path, dialect, sample_size):
    book = xlrd.open_workbook(path, on_demand=True)
    sheet = book.sheet_by_index(0)

    samples = []

    for i in range(1, min(sheet.nrows, sample_size + 1)):
        values = sheet.row_values(i)
        types = sheet.row_types(i)

        values = [normalize_date(v, book.datemode) if t == xlrd.biffh.XL_CELL_DATE else v for v, t in zip(values, types)]

        samples.append(values)

    return samples

