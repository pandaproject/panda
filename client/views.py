#!/usr/bin/env python

import os
import re
from urllib import unquote

from django.contrib.auth.models import User
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

def _get_total_disk_space(p):
    """
    Calculate the total disk space of the device on which a given file path resides.
    """
    s = os.statvfs(p)
    return s.f_frsize * s.f_blocks   

def _get_free_disk_space(p):
    """
    Returns the number of free bytes on the drive that ``p`` is on
    """
    s = os.statvfs(p)
    return s.f_frsize * s.f_bavail

def dashboard(request):
    """
    Render HTML for dashboard/metrics view.
    """
    # Datasets
    dataset_count = Dataset.objects.all().count()

    datasets_without_descriptions = [(unquote(dataset['name']), dataset['slug']) for dataset in Dataset.objects.filter(description='').values('name', 'slug')]
    datasets_without_categories = [(unquote(dataset['name']), dataset['slug']) for dataset in Dataset.objects.filter(categories=None).values('name', 'slug')]

    # Users
    user_count = User.objects.all().count()
    inactive_user_count = User.objects.filter(is_active=False).count()

    foo="""most_active_users = \
        User.objects.all() \
        .annotate(Count('datasets')) \
        .filter(datasets__count__gt=0) \
        .order_by('-datasets__count')[:10]
    
    least_active_users = \
        User.objects.all() \
        .annotate(Count('datasets')) \
        .exclude(id__in=[user.id for user in most_active_users]) \
        .order_by('datasets__count')[:10]"""

    most_active_users = \
        User.objects.all() \
        .annotate(Count('activity_logs')) \
        .filter(activity_logs__count__gt=0) \
        .order_by('-activity_logs__count')[:10]

    least_active_users = \
        User.objects.all() \
        .annotate(Count('activity_logs')) \
        .exclude(id__in=[user.id for user in most_active_users]) \
        .order_by('activity_logs__count')[:10]

    # Disk space
    root_disk = os.stat('/').st_dev
    upload_disk = os.stat(settings.MEDIA_ROOT).st_dev
    indices_disk = os.stat(settings.SOLR_DIRECTORY).st_dev

    root_disk_total = _get_total_disk_space('/')
    root_disk_free = _get_free_disk_space('/')
    root_disk_percent_used = 100 - (float(root_disk_free) / root_disk_total * 100)

    if upload_disk != root_disk:    
        upload_disk_total = _get_total_disk_space(settings.MEDIA_ROOT)
        upload_disk_free = _get_free_disk_space(settings.MEDIA_ROOT)
        upload_disk_percent_used = 100 - (float(upload_disk_free) / upload_disk_total * 100)
    else:
        upload_disk_total = None
        upload_disk_free = None
        upload_disk_percent_used = None

    if indices_disk != root_disk:
        indices_disk_total = _get_total_disk_space(settings.SOLR_DIRECTORY)
        indices_disk_free = _get_free_disk_space(settings.SOLR_DIRECTORY)
        indices_disk_percent_used = 100 - (float(indices_disk_free) / indices_disk_total * 100)
    else:
        indices_disk_total = None
        indices_disk_free = None
        indices_disk_percent_used = None

    return render_to_response('dashboard.html', {
        'dataset_count': dataset_count,
        'datasets_without_descriptions': datasets_without_descriptions,
        'datasets_without_categories': datasets_without_categories,
        'user_count': user_count,
        'inactive_user_count': inactive_user_count,
        'most_active_users': most_active_users,
        'least_active_users': least_active_users,
        'root_disk_total': root_disk_total,
        'root_disk_free': root_disk_free,
        'root_disk_percent_used': root_disk_percent_used,
        'upload_disk_total': upload_disk_total,
        'upload_disk_free': upload_disk_free,
        'upload_disk_percent_used': upload_disk_percent_used,
        'indices_disk_total': indices_disk_total,
        'indices_disk_free': indices_disk_free,
        'indices_disk_percent_used': indices_disk_percent_used
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

