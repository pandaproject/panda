#!/usr/bin/env python

"""
Example showing how to import data from the Public Google Spreadsheet.
"""

import json
from StringIO import StringIO

from csvkit import CSVKitReader
import requests

PANDA_API = 'http://localhost:8000/api/1.0'
PANDA_AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
PANDA_DATASET_SLUG = 'news-developer-jobs'

PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_BULK_UPDATE_SIZE = 1000

SPREADSHEET_ID = '0AmqohgGX3YQadE1VSktrWG1nNFF6RUFNT1RKa0k0a2c'
COLUMNS = ['Employer', 'Date Entered', 'More Info', 'Job Title', 'City / State', 'Contact person', 'Contact email / phone', 'Country', 'Latitude', 'Longitude']

# Utility functions
def panda_get(url, params={}):
    params.update(PANDA_AUTH_PARAMS)
    return requests.get(url, params=params)

def panda_put(url, data, params={}):
    params.update(PANDA_AUTH_PARAMS)
    return requests.put(url, data, params=params, headers={ 'Content-Type': 'application/json' })

def panda_delete(url, params={}):
    params.update(PANDA_AUTH_PARAMS)
    return requests.delete(url, params=params)

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'Google Docs: News Developer Jobs',
        'description': 'The crowdsourced jobs list that powers http://www.newsnerdjobs.com/.'
    }

    response = panda_put(PANDA_DATASET_URL, json.dumps(dataset), params={ 'columns': ','.join(COLUMNS) })

# Open connection to Google
response = requests.get('https://docs.google.com/spreadsheet/pub?key=%s&single=true&gid=4&output=csv' % SPREADSHEET_ID)
csv = StringIO(response.content)

reader = CSVKitReader(csv)
reader.next()

put_data = {
    'objects': []
}

# Delete existing data in panda
response = panda_delete(PANDA_DATA_URL)

for i, row in enumerate(reader):
    put_data['objects'].append({
        'data': row
    })

    if i and i % PANDA_BULK_UPDATE_SIZE == 0:
        print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

        panda_put(PANDA_DATA_URL, json.dumps(put_data))
        put_data['objects'] = []
        
if put_data['objects']:
    print 'Updating %i rows' % len(put_data['objects'])
    panda_put(PANDA_DATA_URL, json.dumps(put_data))

print 'Done'

