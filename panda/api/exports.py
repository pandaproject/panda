#!/usr/bin/env python

from mimetypes import guess_type

from django.conf.urls.defaults import url
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.utils.urls import trailing_slash

from panda.api.utils import PandaApiKeyAuthentication, PandaModelResource, PandaSerializer
from panda.models import Export

class ExportResource(PandaModelResource):
    """
    API resource for Exports.
    """
    from panda.api.users import UserResource

    creator = fields.ForeignKey(UserResource, 'creator')
    dataset = fields.ForeignKey('panda.api.datasets.DatasetResource', 'dataset')

    class Meta:
        queryset = Export.objects.all()
        resource_name = 'export'
        allowed_methods = ['get']

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('download'), name='api_download_export'),
        ]

    def download(self, request, **kwargs):
        """
        Download the original file that was uploaded.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'pk' in kwargs:
            get_id = kwargs['pk']
        else:
            get_id = request.GET.get('id', '')

        export = Export.objects.get(id=get_id)
        path = export.get_path()

        self.log_throttled_access(request)

        response = HttpResponse(FileWrapper(open(path, 'r')), content_type=guess_type(export.filename)[0])
        response['Content-Disposition'] = 'attachment; filename=%s' % export.filename
        response['Content-Length'] = export.size

        return response

