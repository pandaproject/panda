#!/usr/bin/env python

from django.conf.urls.defaults import include, patterns, url
from tastypie.api import Api
from tastypie.utils.urls import trailing_slash

from redd.api import DataResource, DatasetResource, NotificationResource, TaskResource, UploadResource, UserResource
from redd import views

api_1_0 = Api(api_name='1.0')
api_1_0.register(DatasetResource())
api_1_0.register(DataResource())
api_1_0.register(NotificationResource())
api_1_0.register(TaskResource())
api_1_0.register(UploadResource())
api_1_0.register(UserResource())

urlpatterns = patterns('',
    url(r'^login%s$' % trailing_slash(), views.panda_login, name="login"),
    url(r'^register%s$' % trailing_slash(), views.panda_register, name="register"),
    url(r'^upload%s$' % trailing_slash(), views.upload, name="upload"),

    (r'^api/', include(api_1_0.urls)),
)

