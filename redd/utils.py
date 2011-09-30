#!/usr/bin/env python

from itertools import islice

from csvkit import CSVKitReader
from csvkit.typeinference import normalize_table

def infer_types(f, sample_size=100):
    reader = CSVKitReader(f)
    headers = reader.next()

    first_hundred = islice(reader, sample_size)
    normal_types, normal_values = normalize_table(first_hundred, len(headers))

    return zip(headers, [t.__name__ for t in normal_types])
