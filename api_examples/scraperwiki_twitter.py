#!/usr/bin/env python

"""
Example showing how to import Twitter data from the Scraperwiki API.
"""

import json

import requests

PANDA_API = 'http://localhost:8000/api/1.0'
PANDA_AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
PANDA_DATASET_SLUG = 'twitter-pandaproject'

PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_BULK_UPDATE_SIZE = 1000

SCRAPERWIKI_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsonlist&name=basic_twitter_scraper_437&query=select%20*%20from%20%60swdata%60'
COLUMNS = ['text', 'id', 'from_user']

# Utility functions
def panda_get(url, params={}):
    params.update(PANDA_AUTH_PARAMS)
    return requests.get(url, params=params)

def panda_put(url, data, params={}):
    params.update(PANDA_AUTH_PARAMS)
    return requests.put(url, data, params=params, headers={ 'Content-Type': 'application/json' })

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'PANDA Project Twitter Search',
        'description': 'Results of the scraper at <a href="https://scraperwiki.com/scrapers/basic_twitter_scraper_437/">https://scraperwiki.com/scrapers/basic_twitter_scraper_437/</a>.'
    }

    response = panda_put(PANDA_DATASET_URL, json.dumps(dataset), params={
        'columns': ','.join(COLUMNS),
    })

# Fetch latest data from Scraperwiki
print 'Fetching latest data'
response = requests.get(SCRAPERWIKI_URL)

data = json.loads(response.content)

put_data = {
    'objects': []
}

for i, row in enumerate(data['data']):
    put_data['objects'].append({
        'data': row,
        'external_id': unicode(row[1])
    })

    if i and i % PANDA_BULK_UPDATE_SIZE == 0:
        print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

        panda_put(PANDA_DATA_URL, json.dumps(put_data))
        put_data['objects'] = []
        
if put_data['objects']:
    print 'Updating %i rows' % len(put_data['objects'])
    response = panda_put(PANDA_DATA_URL, json.dumps(put_data))

print 'Done'

