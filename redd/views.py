#!/usr/bin/env python

from django.http import HttpResponse
from sunburnt import SolrInterface

from redd.tasks import add 

def test_task(request):
    result = add.delay(4, 4)
    result.get()

    return HttpResponse(result.get())

def test_solr(request):
    solr = SolrInterface('http://localhost:8983')
    solr.add({ 'test': 'test' })
    solr.commit()

    return HttpResponse('Success')

