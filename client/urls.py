#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url

from client import views

urlpatterns = patterns('',
    url(r'^templates.js$', views.jst, name='jst'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^$', views.index, name='index')
)

