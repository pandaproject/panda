#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect
from csvkit.typeinference import normalize_table
from django.conf import settings

def sniff(f):
    return sniff_dialect(f.read(settings.PANDA_SNIFFER_MAX_SAMPLE_SIZE))

def infer_schema(f, dialect, sample_size=100):
    reader = CSVKitReader(f, **dialect)
    headers = reader.next()

    sample = islice(reader, sample_size)
    normal_types, normal_values = normalize_table(sample)
    type_names = [t.__name__ for t in normal_types]

    return [{
        'column': h,
        'simple_type': t,
        'meta_type': None,
        'indexed': False
    } for h, t in zip(headers, type_names)]

def sample_data(f, dialect, sample_size=5):
    reader = CSVKitReader(f, **dialect)
    headers = reader.next()
        
    samples = []

    for i, row in enumerate(islice(reader, sample_size), start=1):
        samples.append({
            'row': i, 
            'data': row,
        })

    return samples 

