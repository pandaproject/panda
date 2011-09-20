from django.conf.urls.defaults import include, patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('redd.urls')),
    (r'^admin/', include(admin.site.urls)),
)
