#!/usr/bin/env python

import datetime

import xlrd

def sniff_dialect(path, **kwargs):
    return {} 

def extract_column_names(path, dialect, **kwargs):
    book = xlrd.open_workbook(path, on_demand=True)
    sheet = book.sheet_by_index(0)
    headers = sheet.row_values(0)

    return headers

def normalize_date(v, datemode):
    """
    Convert an xldate to a date, time, or datetime
    depending on its value.
    """
    v_tuple = xlrd.xldate_as_tuple(v, datemode)

    if v_tuple == (0, 0, 0, 0, 0, 0):
        # Midnight 
        dt = datetime.time(*v_tuple[3:])
    elif v_tuple[3:] == (0, 0, 0):
        # Date only
        dt = datetime.date(*v_tuple[:3])
    elif v_tuple[:3] == (0, 0, 0):
        # Time only
        dt = datetime.time(*v_tuple[3:])
    else:
        # Date and time
        dt = datetime.datetime(*v_tuple)

    return dt.isoformat()

def sample_data(path, dialect, sample_size, **kwargs):
    book = xlrd.open_workbook(path, on_demand=True)
    sheet = book.sheet_by_index(0)

    samples = []

    for i in range(1, min(sheet.nrows, sample_size + 1)):
        values = sheet.row_values(i)
        types = sheet.row_types(i)

        normal_values = []

        for v, t in zip(values, types):
            if t == xlrd.biffh.XL_CELL_DATE:
                v = normalize_date(v, book.datemode)
            elif t == xlrd.biffh.XL_CELL_NUMBER:
                if v % 1 == 0:
                    v = int(v)

            normal_values.append(unicode(v))

        samples.append(normal_values)

    return samples

