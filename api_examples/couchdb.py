#!/usr/bin/env python

"""
Example showing how to import data from the Socrata API.
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

COUCHDB_ROWS_URL = 'http://datacouch.com/db/dc07acde3002cb1f62a08de546916097cd/rows'
COUCHDB_CHANGES_URL = 'http://datacouch.com/db/dc07acde3002cb1f62a08de546916097cd/_changes'

# Utility functions
def panda_get(url):
    return requests.get(url, params=PANDA_AUTH_PARAMS)

def panda_put(url, data):
    return requests.put(url, data, params=PANDA_AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'CouchDB Example',
        'description': 'Blah',
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

    # Do a complete import of all data from CouchDB 
    response = requests.get(COUCHDB_ROWS_URL)
    data = json.loads(response.content)

    put_data = {
        'objects': []
    }

    for i, row in enumerate(data['rows']):
        put_data['objects'].append({
            'data': [row['value']['first_name'], row['value']['last_name'], row['value']['employer']],
            'external_id': row['value']['_id'] 
        })

        if i and i % PANDA_BULK_UPDATE_SIZE == 0:
            print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

            panda_put(PANDA_DATA_URL, json.dumps(put_data))
            put_data['objects'] = []
            
    if put_data['objects']:
        print 'Updating %i rows' % len(put_data['objects'])
        panda_put(PANDA_DATA_URL, json.dumps(put_data))

    print 'Done'

# Fetch changes from CouchDB
#print 'Fetching latest data'
#response = requests.get(COUCHDB_CHANGES_URL)

#data = json.loads(response.content)




