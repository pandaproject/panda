#!/usr/bin/env python

from django.conf import settings
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response

def search(request):
    """
    Simples search UI.
    """
    return render_to_response('search.html', {
        'MEDIA_URL': settings.MEDIA_URL
        }) 

def upload(request):
    """
    UI for uploading a file.
    """
    return render_to_response('upload.html', {
        'MEDIA_URL': settings.MEDIA_URL,
        'csrf_token': get_token(request)
        }) 

