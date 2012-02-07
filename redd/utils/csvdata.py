#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect as csvkit_sniff
from django.conf import settings

from redd.exceptions import DataSamplingError, NotSniffableError

def sniff_dialect(path):
    with open(path, 'r') as f:
        csv_dialect = csvkit_sniff(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))

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

def extract_column_names(path, dialect):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, **dialect)
        headers = reader.next()

        return headers

def sample_data(path, dialect, sample_size):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, **dialect)

        try:
            reader.next() # skip headers
        except UnicodeDecodeError:
            raise DataSamplingError('The header of this CSV file contains characters that are not UTF-8 encoded. PANDA supports only UTF-8 and UTF-8 compatible encodings for CSVs.')

        try:  
            samples = []

            for row in islice(reader, sample_size):
                samples.append(row)
        except UnicodeDecodeError:
            raise DataSamplingError('Row %i of this CSV file contains characters that are not UTF-8 encoded. PANDA supports only UTF-8 and UTF-8 compatible encodings for CSVs.' % (len(samples) + 1))

        return samples 

