#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect
from csvkit.typeinference import normalize_table
from django.conf import settings

def sniff(f):
    return sniff_dialect(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))

def infer_schema(path, dialect, sample_size):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, **dialect)
        headers = reader.next()

        sample = islice(reader, sample_size)
        normal_types, normal_values = normalize_table(sample)
        type_names = [t.__name__ for t in normal_types]

        return [{
            'column': h,
            'type': t
        } for h, t in zip(headers, type_names)]

def sample_data(path, dialect, sample_size):
    with open(path, 'r') as f:
        reader = CSVKitReader(f, **dialect)
        reader.next() # skip headers
            
        samples = []

        for row in islice(reader, sample_size):
            samples.append(row)

        return samples 

