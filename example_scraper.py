#!/usr/bin/env python

import json

import requests

API = 'http://localhost:8000/api/1.0'
AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
DATASET_SLUG = 'foia-request-log-311'

DATA_URL = 'http://data.cityofchicago.org/api/views/j2p9-gdf5/rows.json'

# Check if dataset exists
response = requests.get(API + '/dataset/%s/' % DATASET_SLUG, params=AUTH_PARAMS)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'FOIA Request Log - Office of the Mayor',
        'description': 'FOIA requests made to the mayor\'s office.',
        'schema': [{
            'column': 'Requestor Name',
            'type': 'unicode'
        }, {
            'column': 'Organization',
            'type': 'unicode'
        }, {
            'column': 'Description of Request',
            'type': 'unicode'
        }, {
            'column': 'Date Received',
            'type': 'unicode'
        }, {
            'column': 'Due Date',
            'type': 'unicode'
        }]
    }

    response = requests.put(API + '/dataset/%s/' % DATASET_SLUG, json.dumps(dataset), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

def bulk_update(data):
    requests.put(API + '/dataset/%s/data/' % DATASET_SLUG, json.dumps(data), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

# Fetch latest data from Socrata
response = requests.get(DATA_URL)

data = json.loads(response.content)

put_data = {
    'objects': []
}

for i, row in enumerate(data['data']):
    # First 8 columns are metadata
    put_data['objects'].append({
        'data': row[-5:],
        'external_id': row[0]   # per-dataset id
    })

    if i % 100 == 0:
        print 'Updating 100 rows...'

        bulk_update(put_data)
        put_data['objects'] = []
        
if put_data['objects']:
    'Updating %i rows' % len(put_data['objects'])
    bulk_update(put_data)

