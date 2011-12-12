#!/usr/bin/env python

import json

import requests

API = 'http://localhost:8000/api/1.0'
AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}

# Create dataset
dataset = {
    'name': 'Test Dataset from API',
    'schema': [{
        'column': 'A',
        'simple_type': 'unicode',
        'meta_type': None,
        'indexed': False
    }, {
        'column': 'B',
        'simple_type': 'unicode',
        'meta_type': None,
        'indexed': False
    }, {
        'column': 'C',
        'simple_type': 'unicode',
        'meta_type': None,
        'indexed': False
    }]
}

response = requests.post(API + '/dataset/', json.dumps(dataset), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

dataset = json.loads(response.content)

# Write data
data = {
    'data': ['1', '2', '3']
}

response = requests.post(API + '/dataset/%s/data/' % dataset['slug'], json.dumps(data), params=AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

print response.content
