#!/usr/bin/env python

"""
Ultra-lightweight wrapper around Solr's JSON API.

Replaces sunburnt in PANDA. Not a generic solution.
"""

from django.conf import settings
from django.utils import simplejson as json
import requests

def add(documents, core=settings.SOLR_DATA_CORE, commit=False):
    """
    Add a document or list of documents to Solr.

    Does not commit changes by default.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    params = { 'commit': 'true' } if commit else {}
    requests.post(url, json.dumps(documents), params=params, headers={ 'Content-Type': 'application/json' })

def commit(core=settings.SOLR_DATA_CORE):
    """
    Commit all staged changes to the Solr index.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    requests.post(url, '[]', params={ 'commit': 'true' }, headers={ 'Content-Type': 'application/json' })

def delete(q, core=settings.SOLR_DATA_CORE, commit=True):
    """
    Delete documents by query from the Solr index.

    Commits changes by default.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    params = { 'commit': 'true' } if commit else {}
    requests.post(url, json.dumps({ 'delete': { 'query': q } }), params=params, headers={ 'Content-Type': 'application/json' })

def query(q, core=settings.SOLR_DATA_CORE, limit=10, offset=0, sort='row asc'):
    """
    Execute a simple, raw query against the Solr index.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/select'])
    response = requests.get(url, params={ 'q': q, 'start': offset, 'rows': limit, 'sort': sort }, headers={ 'Content-Type': 'application/json' })

    # TODO: handle error status codes

    return json.loads(response.read())

def query_grouped(q, group_field, core=settings.SOLR_DATA_CORE, limit=10, offset=0, sort='row asc', group_limit=settings.PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP, group_offset=0):
    """
    Execute a query and return results in a grouped format
    appropriate for the PANDA API.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/select'])
    response = requests.get(url, params={ 'q': q, 'start': offset, 'rows': limit, 'sort': sort, 'group': 'true', 'group.field': group_field, 'group.limit': group_limit, 'group.offset': group_offset }, headers={ 'Content-Type': 'application/json' })

    # TODO: handle errors

    return json.loads(response.read())

