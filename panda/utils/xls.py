#!/usr/bin/env python

import datetime
from types import NoneType

from csvkit.convert.xls import determine_column_type
import xlrd

from panda.exceptions import TypeInferenceError

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

def determine_number_type(values):
    """
    Determine if a column of numbers in an XLS file are integral.
    """
    # Test if all values are whole numbers, if so coerce floats it ints
    integral = True

    for v in values:
        if v and v % 1 != 0:
            integral = False
            break

    if integral:
        return int
    else:
        return float

def guess_column_types(path, dialect, sample_size, encoding='utf-8'):
    """
    Guess column types based on a sample of data.
    """
    book = xlrd.open_workbook(path, on_demand=True)
    sheet = book.sheet_by_index(0)

    column_types = []

    for i in range(sheet.ncols):
        values = sheet.col_values(i)[1:sample_size + 1]
        types = sheet.col_types(i)[1:sample_size + 1]
        nominal_type = determine_column_type(types)

        if nominal_type == xlrd.biffh.XL_CELL_EMPTY:
            column_types.append(NoneType)
        elif nominal_type == xlrd.biffh.XL_CELL_TEXT:
            column_types.append(unicode)
        elif nominal_type == xlrd.biffh.XL_CELL_NUMBER:
            column_types.append(determine_number_type(values))
        elif nominal_type == xlrd.biffh.XL_CELL_DATE:
            column_types.append(datetime.datetime)
        elif nominal_type == xlrd.biffh.XL_CELL_BOOLEAN:
            column_types.append(bool)
        elif nominal_type == xlrd.biffh.XL_CELL_ERROR:
            column_types.append(unicode)
        else:
            raise TypeInferenceError('Unknown column type found in xls file: %s' % nominal_type) 

    return [t.__name__ for t in column_types]

