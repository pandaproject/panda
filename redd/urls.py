#!/usr/bin/env python

from django.conf.urls.defaults import patterns, url 
from redd import views

urlpatterns = patterns('',
    url(r'^test_task$', views.test_task, name="test_task"),
)
