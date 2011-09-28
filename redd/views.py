#!/usr/bin/env python

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from sunburnt import SolrInterface

from redd.forms import UploadForm
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

def handle_uploaded_file(f):
    with open('/tmp/test', 'wb+') as output:
        for chunk in f.chunks():
            output.write(chunk)

def test_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
    else:
        form = UploadForm()

    return render_to_response('test_upload.html', RequestContext(request, { 'form': form }))

