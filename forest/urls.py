#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url
from tastypie.utils.urls import trailing_slash

from forest import views

urlpatterns = patterns('',
    url(r'^search%s$' % trailing_slash(), views.search, name='search'),
    url(r'^upload%s$' % trailing_slash(), views.upload, name='upload'),
    url(r'^templates.js$', views.jst, name='jst'),
    url(r'^$', views.index, name='index')
)

