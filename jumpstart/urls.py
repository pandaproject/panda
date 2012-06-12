#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url

from jumpstart import views

urlpatterns = patterns('',
    url(r'^$', views.jumpstart, name='jumpstart')
)

