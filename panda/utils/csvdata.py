#!/usr/bin/env python

import codecs
from itertools import islice
from types import NoneType

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect as csvkit_sniff
from csvkit.typeinference import normalize_table
from django.conf import settings

from panda.exceptions import DataSamplingError, NotSniffableError

def sniff_dialect(path, encoding='utf-8'):
    with codecs.open(path, 'r', encoding=encoding) as f:
        try:
            csv_dialect = csvkit_sniff(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))
        except UnicodeDecodeError:
            raise DataSamplingError('This CSV file contains characters that are not %s encoded. You need to input the correct encoding in order to import data from this file.' % (encoding))

        if not csv_dialect:
            raise NotSniffableError('CSV dialect could not be automatically inferred.') 

        return {
            'lineterminator': csv_dialect.lineterminator,
            'skipinitialspace': csv_dialect.skipinitialspace,
            'quoting': csv_dialect.quoting,
            'delimiter': csv_dialect.delimiter,
            'quotechar': csv_dialect.quotechar,
            'doublequote': csv_dialect.doublequote
        }

def extract_column_names(path, dialect_parameters, encoding='utf-8'):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, encoding=encoding, **dialect_parameters)

        try:
            headers = reader.next()
        except UnicodeDecodeError:
            raise DataSamplingError('This CSV file contains characters that are not %s encoded. You need to input the correct encoding in order to import data from this file.' % encoding)

        return headers

def sample_data(path, dialect_parameters, sample_size, encoding='utf-8'):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, encoding=encoding, **dialect_parameters)

        try:
            reader.next() # skip headers
            samples = []

            for row in islice(reader, sample_size):
                samples.append(row)
        except UnicodeDecodeError:
            raise DataSamplingError('This CSV file contains characters that are not %s encoded. You need to input the correct encoding in order to import data from this file.' % (encoding))

        return samples

def guess_column_types(path, dialect, sample_size, encoding='utf-8'):
    """
    Guess column types based on a sample of data.
    """
    with open(path, 'r') as f:
        reader = CSVKitReader(f, encoding=encoding, **dialect)
        headers = reader.next()

        sample = islice(reader, sample_size)
        normal_types, normal_values = normalize_table(sample)

        type_names = []

        for t in normal_types:
            if t is NoneType:
                type_names.append(None)
            else:
                type_names.append(t.__name__)

        # If a final column had no values csvkit will have dropped it
        while len(type_names) < len(headers):
            type_names.append(None)

        return type_names 

