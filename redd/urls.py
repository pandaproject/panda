#!/usr/bin/env python

from django.conf.urls.defaults import include, patterns, url
from tastypie.api import Api
from tastypie.utils.urls import trailing_slash

from redd.api import DataResource, DatasetResource, TaskResource, UploadResource
from redd import views

api_1_0 = Api(api_name='1.0')
api_1_0.register(TaskResource())
api_1_0.register(UploadResource())
api_1_0.register(DatasetResource())
api_1_0.register(DataResource())

urlpatterns = patterns('',
    url(r'^upload%s$' % trailing_slash(), views.ajax_upload, name="ajax_upload"),

    (r'^api/', include(api_1_0.urls)),
)

