#!/usr/bin/env python

import os
import re

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from tastypie.serializers import Serializer

from redd.api.category import CategoryResource
from redd.models import Category

def index(request):
    """
    Page shell for the client-side application.

    Bootstraps read-once data onto the page.
    """
    serializer = Serializer()
    cr = CategoryResource()

    categories = Category.objects.all()

    bundles = [cr.build_bundle(obj=c) for c in categories]
    categories = [cr.full_dehydrate(b) for b in bundles]

    return render_to_response('index.html', {
        'STATIC_URL': settings.STATIC_URL,
        'bootstrap_data': serializer.to_json({
            'categories': categories
        })
    })

def jst(request):
    """
    Compile JST templates into a javascript module.
    """
    templates_path = os.path.join(settings.SITE_ROOT, 'forest/static/templates')

    compiled = ''

    for dirpath, dirnames, filenames in os.walk(templates_path):
        for filename in filenames:
            name, extension = os.path.splitext(filename)

            if extension != '.jst':
                continue

            fullpath = os.path.join(dirpath, filename)

            with open(fullpath, 'r') as f:
                contents = f.read()

            # Borrowed from django-pipeline
            contents = re.sub(r"\r?\n", "", contents)
            contents = re.sub(r"'", "\\'", contents)

            compiled += "PANDA.templates['%s'] = _.template('%s');\n" % (
                name,
                contents
            )

    return HttpResponse(compiled, mimetype='text/javascript')

