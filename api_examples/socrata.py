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
PANDA_DATASET_SLUG = 'foia-request-log-311'

PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_BULK_UPDATE_SIZE = 100

SOCRATA_URL = 'http://data.cityofchicago.org/api/views/j2p9-gdf5/rows.json?unwrapped=true'

# Utility functions
def panda_get(url):
    return requests.get(url, params=PANDA_AUTH_PARAMS)

def panda_put(url, data):
    return requests.post(url, data, params=PANDA_AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

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

    response = panda_put(PANDA_DATASET_URL, json.dumps(dataset))

# Fetch latest data from Socrata
print 'Fetching latest data'
response = requests.get(SOCRATA_URL)

data = json.loads(response.content)

put_data = {
    'objects': []
}

for i, row in enumerate(data):
    # First 8 columns are metadata
    put_data['objects'].append({
        'data': row[-5:],
        'external_id': unicode(row[0])   # per-dataset id
    })

    if i % PANDA_BULK_UPDATE_SIZE == 0:
        print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

        panda_put(PANDA_DATA_URL, json.dumps(data))
        put_data['objects'] = []
        
if put_data['objects']:
    print 'Updating %i rows' % len(put_data['objects'])
    panda_put(PANDA_DATA_URL, json.dumps(data))

print 'Done'

