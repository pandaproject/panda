#!/usr/bin/env python

import os
import re
from urllib import unquote

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render_to_response
from livesettings import config_value
from tastypie.serializers import Serializer

from panda.api.category import CategoryResource
from panda.models import Category, Dataset

def index(request):
    """
    Page shell for the client-side application.

    Bootstraps read-once data onto the page.
    """
    serializer = Serializer()
    cr = CategoryResource()

    categories = list(Category.objects.annotate(dataset_count=Count('datasets')))

    bundles = [cr.build_bundle(obj=c) for c in categories]
    categories_bootstrap = [cr.full_dehydrate(b) for b in bundles]

    uncategorized = Category(
        id=settings.PANDA_UNCATEGORIZED_ID,
        slug=settings.PANDA_UNCATEGORIZED_SLUG,
        name=settings.PANDA_UNCATEGORIZED_NAME)
    uncategorized.__dict__['dataset_count'] = Dataset.objects.filter(categories=None).count() 
    uncategorized_bundle = cr.full_dehydrate(cr.build_bundle(obj=uncategorized))

    categories_bootstrap.append(uncategorized_bundle)

    return render_to_response('index.html', {
        'settings': settings,
        'max_upload_size': int(config_value('MISC', 'MAX_UPLOAD_SIZE')),
        'demo_mode': int(config_value('MISC', 'DEMO_MODE')),
        'bootstrap_data': serializer.to_json({
            'categories': categories_bootstrap
        })
    })

def get_size(start_path = '.'):
    """
    TODO - move this somewhere
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def format_size(num):
    """
    TODO - move this and clean it up
    """
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def dashboard(request):
    """
    Render HTML for dashboard/metrics view.
    """
    datasets_without_descriptions = [(unquote(dataset.name), dataset.slug) for dataset in Dataset.objects.filter(description='')]
    datasets_without_categories = [(unquote(dataset.name), dataset.slug) for dataset in Dataset.objects.filter(categories=None)]

    upload_disk_used = format_size(get_size(settings.MEDIA_ROOT))
    indices_disk_used = format_size(get_size(settings.SOLR_DIRECTORY))

    return render_to_response('dashboard.html', {
        'datasets_without_descriptions': datasets_without_descriptions,
        'datasets_without_categories': datasets_without_categories,
        'upload_disk_used': upload_disk_used,
        'indices_disk_used': indices_disk_used
    })

def jst(request):
    """
    Compile JST templates into a javascript module.
    """
    templates_path = os.path.join(settings.SITE_ROOT, 'client/static/templates')

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

