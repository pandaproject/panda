#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin

admin.autodiscover()
admin.site.index_template = 'admin/panda_index.html'

urlpatterns = patterns('',
    (r'', include('redd.urls')),
    (r'', include('forest.urls')),
    (r'^admin/settings/', include('livesettings.urls')),
    (r'^admin/', include(admin.site.urls)),

    # Should never be used in production, as nginx will server these paths
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        { 'document_root': settings.STATIC_ROOT,
            'show_indexes': True }),
)
