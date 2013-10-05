#!/usr/bin/env python

import datetime
import os
import re
from urllib import unquote

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.timezone import now

from livesettings import config_value
from tastypie.serializers import Serializer

from client import utils
from panda.api.category import CategoryResource
from panda.models import ActivityLog, Category, Dataset, SearchLog, UserProxy

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
        'email_enabled': int(config_value('EMAIL', 'EMAIL_ENABLED')),
        'demo_mode_enabled': int(config_value('MISC', 'DEMO_MODE_ENABLED')),
        'bootstrap_data': serializer.to_json({
            'categories': categories_bootstrap
        }),
        'moment_lang_code': settings.MOMENT_LANGUAGE_MAPPING.get(settings.LANGUAGE_CODE, None),
    })

def dashboard(request):
    """
    Render HTML for dashboard/metrics view.
    """
    # Datasets
    dataset_count = Dataset.objects.all().count()

    datasets_without_descriptions = [(unquote(dataset['name']), dataset['slug']) for dataset in Dataset.objects.filter(description='').values('name', 'slug')]
    datasets_without_categories = [(unquote(dataset['name']), dataset['slug']) for dataset in Dataset.objects.filter(categories=None).values('name', 'slug')]

    # Users
    user_count = UserProxy.objects.all().count()
    activated_user_count = UserProxy.objects.filter(is_active=True).count()

    today = now().date()
    thirty_days_ago = today - datetime.timedelta(days=30)

    active_users = list(UserProxy.objects.raw('SELECT auth_user.*, count(panda_activitylog.id) AS activity_logs__count FROM auth_user LEFT JOIN panda_activitylog ON panda_activitylog.user_id = auth_user.id WHERE auth_user.is_active = True AND panda_activitylog.when > %s GROUP BY auth_user.id ORDER BY activity_logs__count DESC, auth_user.id ASC', [thirty_days_ago]))

    most_active_users = active_users[:10]

    if len(active_users) > 10:
        least_active_users = active_users[-10:]
        least_active_users.reverse()
    else:
        least_active_users = []

    inactive_users = UserProxy.objects.all() \
        .annotate(Count('activity_logs')) \
        .filter(activity_logs__count=0)

    _active_users_by_day = \
        list(ActivityLog.objects.filter(when__gt=thirty_days_ago) \
        .values('when') \
        .annotate(Count('id')) \
        .order_by('when'))

    dates = [thirty_days_ago + datetime.timedelta(days=x) for x in range(0, 31)]

    active_users_by_day = []

    for d in dates:
        if _active_users_by_day and _active_users_by_day[0]['when'] == d:
            _d = _active_users_by_day.pop(0)
            active_users_by_day.append(_d)
        else:
            active_users_by_day.append({ 'when': d, 'id__count': 0 })

    # Searches

    total_searches = SearchLog.objects.count()

    most_searched_datasets = [(unquote(dataset['name']), dataset['slug'], dataset['searches__count']) for dataset in \
        Dataset.objects.all() \
        .annotate(Count('searches')) \
        .filter(searches__count__gt=0) \
        .order_by('-searches__count') \
        .values('name', 'slug', 'searches__count')[:10]]

    _searches_by_day = \
        list(SearchLog.objects.filter(when__gt=thirty_days_ago) \
        .extra(select={ 'day': '"when"::date' }) \
        .values('day') \
        .annotate(Count('when')) \
        .order_by('day'))

    dates = [thirty_days_ago + datetime.timedelta(days=x) for x in range(0, 31)]

    searches_by_day = []

    for d in dates:
        if _searches_by_day and _searches_by_day[0]['day'] == d:
            _d = _searches_by_day.pop(0)
            searches_by_day.append(_d)
        else:
            searches_by_day.append({ 'day': d, 'when__count': 0 })

    # Disk space
    root_disk = os.stat('/').st_dev
    upload_disk = os.stat(settings.MEDIA_ROOT).st_dev
    indices_disk = os.stat(settings.SOLR_DIRECTORY).st_dev

    root_disk_total = utils.get_total_disk_space('/')
    root_disk_free = utils.get_free_disk_space('/')
    root_disk_percent_used = 100 - (float(root_disk_free) / root_disk_total * 100)

    if upload_disk != root_disk:    
        upload_disk_total = utils.get_total_disk_space(settings.MEDIA_ROOT)
        upload_disk_free = utils.get_free_disk_space(settings.MEDIA_ROOT)
        upload_disk_percent_used = 100 - (float(upload_disk_free) / upload_disk_total * 100)
    else:
        upload_disk_total = None
        upload_disk_free = None
        upload_disk_percent_used = None

    if indices_disk != root_disk:
        indices_disk_total = utils.get_total_disk_space(settings.SOLR_DIRECTORY)
        indices_disk_free = utils.get_free_disk_space(settings.SOLR_DIRECTORY)
        indices_disk_percent_used = 100 - (float(indices_disk_free) / indices_disk_total * 100)
    else:
        indices_disk_total = None
        indices_disk_free = None
        indices_disk_percent_used = None

    return render_to_response('dashboard.html', {
        'settings': settings,
        'dataset_count': dataset_count,
        'datasets_without_descriptions': datasets_without_descriptions,
        'datasets_without_categories': datasets_without_categories,
        'user_count': user_count,
        'activated_user_count': activated_user_count,
        'most_active_users': most_active_users,
        'least_active_users': least_active_users,
        'inactive_users': inactive_users,
        'active_users_by_day': active_users_by_day,
        'total_searches': total_searches,
        'most_searched_datasets': most_searched_datasets,
        'searches_by_day': searches_by_day,
        'root_disk_total': root_disk_total,
        'root_disk_free': root_disk_free,
        'root_disk_percent_used': root_disk_percent_used,
        'upload_disk_total': upload_disk_total,
        'upload_disk_free': upload_disk_free,
        'upload_disk_percent_used': upload_disk_percent_used,
        'indices_disk_total': indices_disk_total,
        'indices_disk_free': indices_disk_free,
        'indices_disk_percent_used': indices_disk_percent_used,
        'storage_documentation_url': 'http://panda.readthedocs.org/en/%s/storage.html' % settings.PANDA_VERSION
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

