#!/usr/bin/env python

import os
import re

from django.conf import settings
from django.http import HttpResponse
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

def jst(request):
    """
    Compile JST templates into a javascript module.
    """
    templates_path = os.path.join(settings.SITE_ROOT, 'forest/static/templates')

    compiled = 'var JST; JST = JST || {};\n'

    for dirpath, dirnames, filenames in os.walk(templates_path):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)

            with open(fullpath, 'r') as f:
                contents = f.read()

            # From django-pipeline
            contents = re.sub(r"\r?\n", "", contents)
            contents = re.sub(r"'", "\\'", contents)

            compiled += "JST['%s'] = _.template('%s');\n" % (
                os.path.splitext(filename)[0],
                contents
            )

    return HttpResponse(compiled, mimetype='text/javascript')

