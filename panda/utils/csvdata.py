#!/usr/bin/env python

import codecs
from itertools import islice

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect as csvkit_sniff
from django.conf import settings

from panda.exceptions import DataSamplingError, NotSniffableError

def sniff_dialect(path, encoding='utf-8'):
    with codecs.open(path, 'r', encoding=encoding) as f:
        try:
            csv_dialect = csvkit_sniff(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))
        except UnicodeDecodeError:
            raise DataSamplingError('This CSV file contains characters that are not %s encoded. You need to input the correct encoding in order to import data from this file.' % (settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE, encoding))

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

