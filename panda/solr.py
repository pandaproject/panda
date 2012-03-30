#!/usr/bin/env python

"""
Ultra-lightweight wrapper around Solr's JSON API.

Replaces sunburnt in PANDA. Not a generic solution.
"""
import datetime

from django.conf import settings
from django.utils import datetime_safe
from django.utils import simplejson

import requests

class SolrJSONEncoder(simplejson.JSONEncoder):
    """
    Custom JSONEncoder based on DjangoJSONEncoder that formats datetimes the way Solr likes them. 
    """
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return d.strftime("%sT%sZ" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        else:
            return super(SolrJSONEncoder, self).default(o)

def dumps(data):
    return simplejson.dumps(data, cls=SolrJSONEncoder)

def loads(data):
    return simplejson.loads(data)

class SolrError(Exception):
    """
    Exceptionr raised when a Solr requests fails for any reason.
    """
    def __init__(self, response, *args, **kwargs):
        self.status_code = response.status_code
        self.response_body = response.content

        super(SolrError, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.response_body

def add(core, documents, commit=False):
    """
    Add a document or list of documents to Solr.

    Does not commit changes by default.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    params = { 'commit': 'true' } if commit else {}
    response = requests.post(url, dumps(documents), params=params, headers={ 'Content-Type': 'application/json' })

    if response.status_code != 200:
        raise SolrError(response)
    
    return loads(response.content)

def commit(core):
    """
    Commit all staged changes to the Solr index.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    response = requests.post(url, '[]', params={ 'commit': 'true' }, headers={ 'Content-Type': 'application/json' })

    if response.status_code != 200:
        raise SolrError(response)
    
    return loads(response.content)

def delete(core, q, commit=True):
    """
    Delete documents by query from the Solr index.

    Commits changes by default.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/update'])
    params = { 'commit': 'true' } if commit else {}
    response = requests.post(url, dumps({ 'delete': { 'query': q } }), params=params, headers={ 'Content-Type': 'application/json' })
    
    if response.status_code != 200:
        raise SolrError(response)
    
    return loads(response.content)

def query(core, q, limit=10, offset=0, sort='_docid_ asc'):
    """
    Execute a simple, raw query against the Solr index.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/select'])
    response = requests.get(url, params={ 'q': q, 'start': offset, 'rows': limit, 'sort': sort }, headers={ 'Content-Type': 'application/json' })

    if response.status_code != 200:
        raise SolrError(response)
    
    return loads(response.content)

def query_grouped(core, q, group_field, limit=10, offset=0, sort='_docid_ asc', group_limit=settings.PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP, group_offset=0):
    """
    Execute a query and return results in a grouped format
    appropriate for the PANDA API.
    """
    url = ''.join([settings.SOLR_ENDPOINT, '/', core, '/select'])
    response = requests.get(url, params={ 'q': q, 'start': offset, 'rows': limit, 'sort': sort, 'group': 'true', 'group.field': group_field, 'group.limit': group_limit, 'group.offset': group_offset, 'group.ngroups': 'true' }, headers={ 'Content-Type': 'application/json' })

    if response.status_code != 200:
        raise SolrError(response)

    return loads(response.content)

