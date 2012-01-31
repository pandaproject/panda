#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect as csvkit_sniff
from django.conf import settings

from redd.exceptions import NotSniffableError

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
        reader.next() # skip headers
            
        samples = []

        for row in islice(reader, sample_size):
            samples.append(row)

        return samples 

