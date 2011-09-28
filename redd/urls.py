#!/usr/bin/env python

from django.conf.urls.defaults import include, patterns, url
from tastypie.api import Api

from redd.api import DatasetResource
from redd import views

api_1_0 = Api(api_name='1.0')
api_1_0.register(DatasetResource())

urlpatterns = patterns('',
    url(r'^test_task$', views.test_task, name="test_task"),
    url(r'^test_solr$', views.test_solr, name="test_solr"),
    url(r'^test_upload$', views.test_upload, name="test_upload"),
    (r'^api/', include(api_1_0.urls)),
)

