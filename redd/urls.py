#!/usr/bin/env python

from django.conf.urls.defaults import include, patterns, url
from tastypie.api import Api

from redd.api import DatasetResource
from redd import views

api_1_0 = Api(api_name='1.0')
api_1_0.register(DatasetResource())

urlpatterns = patterns('',
    url(r'^test_task$', views.test_task, name="test_task"),
    (r'^api/', include(api_1_0.urls)),
)

