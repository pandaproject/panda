#!/usr/bin/env python

from django.conf import settings
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response

def search(request):
    """
    Simples search UI.
    """
    return render_to_response('search.html', {
        'STATIC_URL': settings.STATIC_URL
        }) 

def upload(request):
    """
    UI for uploading a file.
    """
    return render_to_response('upload.html', {
        'STATIC_URL': settings.STATIC_URL,
        'csrf_token': get_token(request)
        })

def index(request):
    """
    Page shell for the client-side application.
    """
    return render_to_response('index.html', {
        'STATIC_URL': settings.STATIC_URL,
        'csrf_token': get_token(request)
        })

