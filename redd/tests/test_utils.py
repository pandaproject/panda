#!/usr/bin/env python

import os.path

from django.test import TestCase

from redd import utils
from redd.tests import utils as test_utils

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

    def test_csv_extract_column_names(self):
        columns = utils.csv.extract_column_names(self.path, self.dialect)

        self.assertEqual(columns, ['id', 'first_name', 'last_name', 'employer'])

    def test_csv_sample_data(self):
        samples = utils.csv.sample_data(self.path, self.dialect, 2)

        self.assertEqual(samples, [['1', 'Brian', 'Boyer', 'Chicago Tribune'], ['2', 'Joseph', 'Germuska', 'Chicago Tribune']])

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

