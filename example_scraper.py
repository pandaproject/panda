#!/usr/bin/env python

import json

import requests

API = 'http://localhost:8000/api/1.0'
AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
DATASET_SLUG = 'test-dataset'

# Check if dataset exists
response = requests.get(API + '/dataset/%s/' % DATASET_SLUG, params=AUTH_PARAMS)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'Test Dataset from API',
        'schema': [{
            'column': 'A',
            'type': 'unicode'
        }, {
            'column': 'B',
            'type': 'unicode'
        }, {
            'column': 'C',
            'type': 'unicode'
        }]
    }

    response = requests.put(API + '/dataset/%s/' % DATASET_SLUG, json.dumps(dataset), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

# Write data
data = { 'objects': [{
    'data': ['The', 'PANDA', 'lives.']
}, {
    'data': ['More', 'data', 'here.']   
}]}

response = requests.put(API + '/dataset/%s/data/' % DATASET_SLUG, json.dumps(data), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

