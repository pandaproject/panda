#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url

from forest import views

urlpatterns = patterns('',
    url(r'^templates.js$', views.jst, name='jst'),
    url(r'^$', views.index, name='index')
)

