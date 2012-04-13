#!/usr/bin/env python

from datetime import date, time, datetime
import os.path

from django.test import TestCase

from panda import utils
from panda.exceptions import TypeCoercionError
from panda.tests import utils as test_utils

class TestCSV(TestCase):
    def setUp(self):
        self.path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_DATA_FILENAME)
        self.dialect = {
            'delimiter': ',',
            'doublequote': False,
            'lineterminator': '\r\n',
            'quotechar': '"',
            'quoting': 0,
            'skipinitialspace': False
        }

    def test_csv_sniff_dialect(self):
        dialect = utils.csv.sniff_dialect(self.path)

        self.assertEqual(dialect, self.dialect)

    def test_csv_sniff_dialect_latin1(self):
        path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_LATIN1_FILENAME)

        dialect = utils.csv.sniff_dialect(path, encoding='Latin-1')

        self.assertEqual(dialect, self.dialect)

    def test_csv_extract_column_names(self):
        columns = utils.csv.extract_column_names(self.path, self.dialect)

        self.assertEqual(columns, ['id', 'first_name', 'last_name', 'employer'])

    def test_csv_extract_column_names_latin1(self):
        path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_LATIN1_FILENAME)

        columns = utils.csv.extract_column_names(path, self.dialect, encoding='Latin-1')

        self.assertEqual(columns, ['activity', 'unsupplemented mean', 'dir', 'sem', 'n', 'supplemented mean', 'dir', 'sem'])

    def test_csv_sample_data(self):
        samples = utils.csv.sample_data(self.path, self.dialect, 2)

        self.assertEqual(samples, [['1', 'Brian', 'Boyer', 'Chicago Tribune'], ['2', 'Joseph', 'Germuska', 'Chicago Tribune']])

    def test_csv_sample_data_latin1(self):
        path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_LATIN1_FILENAME)

        samples = utils.csv.sample_data(path, self.dialect, 2, encoding='Latin-1')

        self.assertEqual(samples, [[u'sitting', u'1.21', u'\xb1', u'0.02', u'76', u'1.27', u'\xb1', u'0.02*'], [u'standing', u'1.23', u'\xb1', u'0.03', u'58', u'1.28', u'\xb1', u'0.03']])

    def test_csv_guess_column_types(self):
        guessed_types = utils.csv.guess_column_types(self.path, self.dialect, 5, encoding='Latin-1')

        self.assertEqual(guessed_types, ['int', 'unicode', 'unicode', 'unicode'])

class TestXLS(TestCase):
    def setUp(self):
        self.path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_XLS_FILENAME)
        self.dialect = {}

    def test_xls_sniff_dialect(self):
        dialect = utils.xls.sniff_dialect(self.path)

        self.assertEqual(dialect, self.dialect)

    def test_xls_extract_column_names(self):
        columns = utils.xls.extract_column_names(self.path, self.dialect)

        self.assertEqual(columns, ['id', 'first_name', 'last_name', 'employer'])

    def test_xls_sample_data(self):
        samples = utils.xls.sample_data(self.path, self.dialect, 2)

        self.assertEqual(samples, [['1', 'Brian', 'Boyer', 'Chicago Tribune'], ['2', 'Joseph', 'Germuska', 'Chicago Tribune']])

    def test_xls_guess_column_types(self):
        self.path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_XLS_TYPES_FILENAME)

        guessed_types = utils.xls.guess_column_types(self.path, self.dialect, 5, encoding='Latin-1')

        self.assertEqual(guessed_types, ['unicode', 'date', 'int', 'bool', 'float', 'time', 'datetime', None, 'unicode'])

class TestXLSX(TestCase):
    def setUp(self):
        self.path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_EXCEL_XLSX_FILENAME)
        self.dialect = {}

    def test_xlsx_sniff_dialect(self):
        dialect = utils.xlsx.sniff_dialect(self.path)

        self.assertEqual(dialect, self.dialect)

    def test_xlsx_extract_column_names(self):
        columns = utils.xlsx.extract_column_names(self.path, self.dialect)

        self.assertEqual(columns, ['id', 'first_name', 'last_name', 'employer'])

    def test_xlsx_sample_data(self):
        samples = utils.xlsx.sample_data(self.path, self.dialect, 2)

        self.assertEqual(samples, [['1', 'Brian', 'Boyer', 'Chicago Tribune'], ['2', 'Joseph', 'Germuska', 'Chicago Tribune']])

    def test_xlsx_guess_column_types(self):
        self.path = os.path.join(test_utils.TEST_DATA_PATH, test_utils.TEST_XLSX_TYPES_FILENAME)

        guessed_types = utils.xlsx.guess_column_types(self.path, self.dialect, 5, encoding='Latin-1')

        self.assertEqual(guessed_types, ['unicode', 'date', 'int', 'bool', 'float', 'time', 'datetime', None, 'unicode'])

class TestTypeCoercion(TestCase):
    def setUp(self):
        self.data_typer = utils.typecoercion.DataTyper([])
        self.coerce_type = self.data_typer.coerce_type

    def test_coerce_nulls(self):
        self.assertEqual(self.coerce_type(None, bool), None)
        self.assertEqual(self.coerce_type('N/A', int), None)
        self.assertEqual(self.coerce_type('n/a', datetime), None)

    def test_coerce_int_from_str(self):
        self.assertEqual(self.coerce_type('171', int), 171)

    def test_coerce_int_from_str_fails(self):
        with self.assertRaises(TypeCoercionError):
            self.assertEqual(self.coerce_type('#171', int), 171)

    def test_coerce_int_from_unicode(self):
        self.assertEqual(self.coerce_type(u'171', int), 171)

    def test_coerce_int_from_currency_str(self):
        self.assertEqual(self.coerce_type('$171,000', int), 171000)

    def test_coerce_int_from_currency_float(self):
        self.assertEqual(self.coerce_type(u'$171,000', int), 171000)

    def test_coerce_float_from_str(self):
        self.assertEqual(self.coerce_type('171.59', float), 171.59)

    def test_coerce_float_from_unicode(self):
        self.assertEqual(self.coerce_type(u'171.59', float), 171.59)

    def test_coerce_float_from_currency_str(self):
        self.assertEqual(self.coerce_type('$171,000.59', float), 171000.59)

    def test_coerce_float_from_currency_float(self):
        self.assertEqual(self.coerce_type(u'$171,000.59', float), 171000.59)

    def test_coerce_bool_from_str(self):
        self.assertEqual(self.coerce_type('True', bool), True)
        self.assertEqual(self.coerce_type('true', bool), True)
        self.assertEqual(self.coerce_type('T', bool), True)
        self.assertEqual(self.coerce_type('yes', bool), True)

    def test_coerce_bool_from_unicode(self):
        self.assertEqual(self.coerce_type(u'True', bool), True)
        self.assertEqual(self.coerce_type(u'true', bool), True)
        self.assertEqual(self.coerce_type(u'T', bool), True)
        self.assertEqual(self.coerce_type(u'yes', bool), True)

    def test_coerce_datetime_from_str(self):
        self.assertEqual(self.coerce_type('2011-4-13 8:28 AM', datetime), datetime(2011, 4, 13, 8, 28, 0))

    def test_coerce_date_from_str(self):
        self.assertEqual(self.coerce_type('2011-4-13', date), datetime(2011, 4, 13, 0, 0, 0))
        
    def test_coerce_time_from_str(self):
        self.assertEqual(self.coerce_type('8:28 AM', time), datetime(9999, 12, 31, 8, 28, 0))

