#!/usr/bin/env python

import datetime

from csvkit.convert.xls import determine_column_type
import xlrd
from django.utils.translation import ugettext as _

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

def determine_date_type(values, datemode=0):
    """
    Determine if an Excel date column really contains dates... 
    """
    normal_types_set = set()

    for v in values:
        # Skip blanks 
        if v == '':
            continue

        v_tuple = xlrd.xldate_as_tuple(v, datemode)

        if v_tuple == (0, 0, 0, 0, 0, 0):
            # Midnight 
            normal_types_set.add(datetime.time)
        elif v_tuple[3:] == (0, 0, 0):
            # Date only
            normal_types_set.add(datetime.date)
        elif v_tuple[:3] == (0, 0, 0):
            # Time only
            normal_types_set.add(datetime.time)
        else:
            # Date and time
            normal_types_set.add(datetime.datetime)

    if len(normal_types_set) == 1:
        # No special handling if column contains only one type
        return normal_types_set.pop()
    elif normal_types_set == set([datetime.datetime, datetime.date]):
        # If a mix of dates and datetimes, up-convert dates to datetimes
        return datetime.datetime
    elif normal_types_set == set([datetime.datetime, datetime.time]):
        # Datetimes and times don't mix
        return unicode
    elif normal_types_set == set([datetime.date, datetime.time]):
        # Dates and times don't mix
        return unicode

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
            column_types.append(None)
        elif nominal_type == xlrd.biffh.XL_CELL_TEXT:
            column_types.append(unicode)
        elif nominal_type == xlrd.biffh.XL_CELL_NUMBER:
            column_types.append(determine_number_type(values))
        elif nominal_type == xlrd.biffh.XL_CELL_DATE:
            column_types.append(determine_date_type(values, datemode=book.datemode))
        elif nominal_type == xlrd.biffh.XL_CELL_BOOLEAN:
            column_types.append(bool)
        elif nominal_type == xlrd.biffh.XL_CELL_ERROR:
            column_types.append(unicode)
        else:
            raise TypeInferenceError(_('Unknown column type found in xls file: %s') % nominal_type) 

    return [t.__name__ if t else None for t in column_types]

