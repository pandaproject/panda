#!/usr/bin/env python

import re
import unicodedata

def slugify(name):
    """
    Slugify a column header for use as a name.

    Adapted from Django.
    """
    slug = name
    slug = unicodedata.normalize('NFKD', unicode(slug)).encode('ascii', 'ignore')
    slug = unicode(re.sub('[^\w\s-]', '', slug).strip().lower())
    slug = re.sub('[-\s]+', '_', slug)

    return slug

def update_indexed_names(column_schema):
    """
    Update a column schema with appropriate indexed column names.
    """
    indexed_names = []

    for i, c in enumerate(column_schema):
        if c['indexed'] and c['type']:
            slug = slugify(c['name'])

            indexed_name = 'column_%s_%s' % (c['type'], slug)

            # Deduplicate within dataset
            if indexed_name in indexed_names:
                n = 2
                test_name = '%s%i' % (indexed_name, n)

                while test_name in indexed_names:
                    n += 1
                    test_name = '%s%i' % (indexed_name, n)

                indexed_name = test_name

            column_schema[i]['indexed_name'] = indexed_name
            indexed_names.append(indexed_name)

    return column_schema 

def make_column_schema(columns, indexed=None, types=None):
    """
    Generate a column schema from parallel arrays of columns, index booleans, and index types.
    """
    column_schema = []

    for i, name in enumerate(columns):
        c = {
            'name': name,
            'indexed': indexed[i] if indexed else False,
            'type': types[i] if types else None,
            'indexed_name': None,
            'min': None,
            'max': None
        }

        column_schema.append(c)

    column_schema = update_indexed_names(column_schema)

    return column_schema

