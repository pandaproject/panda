#!/usr/bin/env python

"""
Example showing how to import data from the Socrata API.
"""

import json
import re

import requests

PANDA_API = 'http://localhost:8000/api/1.0'
PANDA_AUTH_PARAMS = {
    'email': 'panda@pandaproject.net',
    'api_key': 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
}
PANDA_DATASET_SLUG = 'smith-county-criminal-cases'

PANDA_DATASET_URL = '%s/dataset/%s/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_DATA_URL = '%s/dataset/%s/data/' % (PANDA_API, PANDA_DATASET_SLUG)
PANDA_BULK_UPDATE_SIZE = 100

SCRAPERWIKI_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=tyler_criminal_records&query=select%20*%20from%20%60swdata%60'
COLUMNS = ['cause_number', 'date_filed', 'defendant_name', 'defendant_birthdate', 'offense', 'crime_date', 'degree', 'disposed', 'court', 'warrant_status', 'attorney', 'view_url']

# Utility functions
def panda_get(url):
    return requests.get(url, params=PANDA_AUTH_PARAMS)

def panda_put(url, data):
    return requests.put(url, data, params=PANDA_AUTH_PARAMS, headers={ 'Content-Type': 'application/json' })

def slugify(value):
    """
    Graciously borrowed from Django core.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

# Check if dataset exists
response = panda_get(PANDA_DATASET_URL)

# Create dataset if necessary
if response.status_code == 404:
    dataset = {
        'name': 'Smith County Criminal Case Records',
        'description': 'Results of the scraper at <a href="https://scraperwiki.com/scrapers/tyler_criminal_records/">https://scraperwiki.com/scrapers/tyler_criminal_records/</a>.',
        'schema': [{ 'column': c, 'type': 'unicode' } for c in COLUMNS ]
    }

    response = panda_put(PANDA_DATASET_URL, json.dumps(dataset))

# Fetch latest data from Socrata
print 'Fetching latest data'
response = requests.get(SCRAPERWIKI_URL)

data = json.loads(response.content)

put_data = {
    'objects': []
}

for i, row in enumerate(data):
    put_data['objects'].append({
        'data': [row[c] for c in COLUMNS],
        'external_id': slugify(row['cause_number']) # Slugify because a few have errants commas and such
    })

    if i and i % PANDA_BULK_UPDATE_SIZE == 0:
        print 'Updating %i rows...' % PANDA_BULK_UPDATE_SIZE

        panda_put(PANDA_DATA_URL, json.dumps(put_data))
        put_data['objects'] = []
        
if put_data['objects']:
    print 'Updating %i rows' % len(put_data['objects'])
    panda_put(PANDA_DATA_URL, json.dumps(put_data))

print 'Done'

