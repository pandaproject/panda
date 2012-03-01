#!/usr/bin/env python

import os.path

from django.test import TestCase

from panda import utils
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

        self.assertEqual(guessed_types, ['unicode', 'date', 'int', 'bool', 'float', 'time', 'datetime', 'NoneType', 'unicode'])

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
        guessed_types = utils.xlsx.guess_column_types(self.path, self.dialect, 5, encoding='Latin-1')

        self.assertEqual(guessed_types, ['int', 'unicode', 'unicode', 'unicode'])

