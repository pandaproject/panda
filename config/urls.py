#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin

# Jumpstart mode
if settings.SETTINGS == 'jumpstart':
    urlpatterns = patterns('',
        (r'', include('jumpstart.urls')),
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root': settings.STATIC_ROOT,
                'show_indexes': True }),
    )
# Normal mode
else:
    admin.autodiscover()
    admin.site.index_template = 'admin/panda_index.html'

    urlpatterns = patterns('',
        (r'', include('panda.urls')),
        (r'', include('client.urls')),
        (r'^admin/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
        (r'^admin/logout/$', 'django.contrib.auth.views.logout'),
        
        (r'^admin/settings/', include('livesettings.urls')),
        (r'^admin/', include(admin.site.urls)),

        # Should never be used in production, as nginx will server these paths
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root': settings.STATIC_ROOT,
                'show_indexes': True }),
    )
