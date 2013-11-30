#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib import admin

from longerusername.forms import AuthenticationForm

# Jumpstart mode
if settings.SETTINGS == 'jumpstart':
    urlpatterns = patterns('',
        (r'', include('jumpstart.urls')),
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True
        }),
    )
# Normal mode
else:
    admin.autodiscover()
    admin.site.index_template = 'admin/panda_index.html'
    admin.site.login_form = AuthenticationForm

    urlpatterns = patterns('',
        (r'', include('panda.urls')),
        (r'', include('client.urls')),
        (r'^admin/settings/', include('livesettings.urls')),
        (r'^admin/', include(admin.site.urls)),

        # Should never be used in production, as nginx will serve these paths
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True
        }),
    )
