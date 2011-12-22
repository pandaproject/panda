#!/usr/bin/env python

"""
Example showing how to import data from a CouchDB instance.

Uses Couch's _changes feed to propogate updates and deletes into PANDA.
"""

import json

import requests

PANDA_API = 'http://localhost:8000/api/1.0'
PANDA_AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
PANDA_DATASET_SLUG = 'couchdb-example'

PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_BULK_UPDATE_SIZE = 1000

COUCHDB_ROOT_URL = 'http://datacouch.com/db/dc07acde3002cb1f62a08de546916097cd'
COUCHDB_ROWS_URL = 'http://datacouch.com/db/dc07acde3002cb1f62a08de546916097cd/rows'
COUCHDB_CHANGES_URL = 'http://datacouch.com/db/dc07acde3002cb1f62a08de546916097cd/_changes'

LAST_SEQ_FILENAME = 'last_seq'

# Utility functions
def panda_get(url):
    return requests.get(url, params=PANDA_AUTH_PARAMS)

def panda_put(url, data):
    return requests.put(url, data, params=PANDA_AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

def panda_delete(url):
    return requests.delete(url, params=PANDA_AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

def write_last_seq(last_seq):
    with open(LAST_SEQ_FILENAME, 'w') as f:
        f.write(str(last_seq))

def read_last_seq():
    with open(LAST_SEQ_FILENAME) as f:
        return f.read().strip()

def couchdb_row_to_panda_data(row):
    return {
        'data': [row['first_name'], row['last_name'], row['employer']],
        'external_id': row['_id'] 
    }

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'CouchDB: PANDA Contributors',
        'description': 'A list of contributors to PANDA imported from a dataset on DataCouch: <a href="http://datacouch.com/edit/#/dc07acde3002cb1f62a08de546916097cd">http://datacouch.com/edit/#/dc07acde3002cb1f62a08de546916097cd</a>.',
        'schema': [{
            'column': 'First Name',
            'type': 'unicode'
        }, {
            'column': 'Last Name',
            'type': 'unicode'
        }, {
            'column': 'Employer',
            'type': 'unicode'
        }]
    }

    response = panda_put(PANDA_DATASET_URL, json.dumps(dataset))

    # Get changes that have come before so we can skip them in the future
    response = requests.get(COUCHDB_CHANGES_URL)
    data = json.loads(response.content)

    write_last_seq(data['last_seq'])

    # Do a complete import of all data from CouchDB 
    response = requests.get(COUCHDB_ROWS_URL)
    data = json.loads(response.content)

    put_data = {
        'objects': []
    }

    for i, row in enumerate(data['rows']):
        put_data['objects'].append(couchdb_row_to_panda_data(row['value']))

        if i and i % PANDA_BULK_UPDATE_SIZE == 0:
            print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

            panda_put(PANDA_DATA_URL, json.dumps(put_data))
            put_data['objects'] = []
            
    if put_data['objects']:
        print 'Updating %i rows' % len(put_data['objects'])
        panda_put(PANDA_DATA_URL, json.dumps(put_data))

# Update existing dataset
else:
    # Where did we leave off?
    last_seq = read_last_seq()

    response = requests.get(COUCHDB_CHANGES_URL, params={ 'since': last_seq })
    data = json.loads(response.content)
    
    delete_ids = []

    put_data = {
        'objects': []
    }

    for i, row in enumerate(data['results']):
        # Is this a deletion?
        if row.get('deleted', False):
            delete_ids.append(row['id'])
            continue

        doc_id = row['id']

        detail_response = requests.get('%s/%s' % (COUCHDB_ROOT_URL, doc_id))
        detail_data = json.loads(detail_response.content)

        put_data['objects'].append(couchdb_row_to_panda_data(detail_data))

        if i and i % PANDA_BULK_UPDATE_SIZE == 0:
            print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

            panda_put(PANDA_DATA_URL, json.dumps(put_data))
            put_data['objects'] = []
            
    if put_data['objects']:
        print 'Updating %i rows' % len(put_data['objects'])
        panda_put(PANDA_DATA_URL, json.dumps(put_data))

    # Process deletes
    if delete_ids:
        print 'Deleting %i rows' % len(delete_ids)

        for deleted in delete_ids:
            response = panda_delete('%s%s/' % (PANDA_DATA_URL, deleted))

    # Update location for next run
    write_last_seq(data['last_seq'])

print 'Done'

