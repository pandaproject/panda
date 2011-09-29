#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader
from django.conf import settings
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.shortcuts import render_to_response
from sunburnt import SolrInterface

from redd.storage import PANDAUploadBackend
from redd.tasks import add 

def test_task(request):
    result = add.delay(4, 4)
    result.get()

    return HttpResponse(result.get())

def test_solr(request):
    solr = SolrInterface('http://localhost:8983/solr')
    solr.add({
        'dataset_id': '1',
        'id': '1'
    })
    solr.commit()
    return HttpResponse('Success')

def upload(request):
    """
    UI for uploading a file.
    """
    return render_to_response('upload.html', {
        'MEDIA_URL': settings.MEDIA_URL,
        'csrf_token': get_token(request)
        }) 

ajax_upload = AjaxFileUploader(backend=PANDAUploadBackend)

