#!/usr/bin/env python

from django.conf.urls.defaults import include, patterns, url
from tastypie.api import Api
from tastypie.utils.urls import trailing_slash

from panda.api import ActivityLogResource, CategoryResource, DatasetResource, DataUploadResource, ExportResource, NotificationResource, RelatedUploadResource, TaskResource, UserResource
from panda import views

api_1_0 = Api(api_name='1.0')
api_1_0.register(ActivityLogResource())
api_1_0.register(CategoryResource())
api_1_0.register(DatasetResource())
api_1_0.register(DataUploadResource())
api_1_0.register(ExportResource())
api_1_0.register(NotificationResource())
api_1_0.register(RelatedUploadResource())
api_1_0.register(TaskResource())
api_1_0.register(UserResource())

urlpatterns = patterns('',
    url(r'^login%s$' % trailing_slash(), views.panda_login, name="login"),
    url(r'^check_activation_key/(?P<activation_key>[\w\d]+)%s$' % trailing_slash(), views.check_activation_key, name="check_activation_key"),
    url(r'^activate%s$' % trailing_slash(), views.activate, name="activate"),
    url(r'^forgot_password%s$' % trailing_slash(), views.forgot_password, name="forgot_password"),
    url(r'^check_available_space%s$' % trailing_slash(), views.check_available_space, name="check_available_space"),
    url(r'^data_upload%s$' % trailing_slash(), views.data_upload, name="data_upload"),
    url(r'^related_upload%s$' % trailing_slash(), views.related_upload, name="related_upload"),

    (r'^api/', include(api_1_0.urls)),
)

