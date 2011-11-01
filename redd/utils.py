#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.typeinference import normalize_table

def infer_schema(f, sample_size=100):
    reader = CSVKitReader(f)
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

def sample_data(f, sample_size=5):
    reader = CSVKitReader(f)
    headers = reader.next()
        
    samples = []

    for i, row in enumerate(islice(reader, sample_size), start=1):
        samples.append({
            'row': i, 
            'data': row,
        })

    return samples 

