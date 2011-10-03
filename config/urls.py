#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('redd.urls')),
    (r'^tasks/', include('djcelery.urls')),
    (r'^admin/', include(admin.site.urls)),

    # Should never be used in production, as nginx will server these paths
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root': settings.MEDIA_ROOT,
            'show_indexes': True }),
)
