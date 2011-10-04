#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader
from django.conf import settings
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.shortcuts import render_to_response
from sunburnt import SolrInterface

from redd.storage import PANDAUploadBackend

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
    import logging
    import os
    logger = logging.getLogger(__name__)
    logger.error(os.environ['DEPLOYMENT_TARGET'])

    return render_to_response('upload.html', {
        'MEDIA_URL': settings.MEDIA_URL,
        'csrf_token': get_token(request)
        }) 

ajax_upload = AjaxFileUploader(backend=PANDAUploadBackend)

def search(request):
    """
    Simples search UI.
    """
    return render_to_response('search.html', {
        'MEDIA_URL': settings.MEDIA_URL
        }) 

