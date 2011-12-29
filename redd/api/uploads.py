#!/usr/bin/env python

from mimetypes import guess_type

from django.conf.urls.defaults import url
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.utils.urls import trailing_slash

from redd.api.utils import CustomApiKeyAuthentication, CustomResource, CustomSerializer
from redd.models import Upload

class UploadResource(CustomResource):
    """
    API resource for Uploads.
    """
    #from redd.api.datasets import DatasetResource
    from redd.api.users import UserResource

    creator = fields.ForeignKey(UserResource, 'creator')
    dataset = fields.ForeignKey('redd.api.datasets.DatasetResource', 'dataset')

    class Meta:
        queryset = Upload.objects.all()
        resource_name = 'upload'
        allowed_methods = ['get']

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('download'), name='api_download_upload'),
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

        upload = Upload.objects.get(id=get_id)
        path = upload.get_path()

        self.log_throttled_access(request)

        response = HttpResponse(FileWrapper(open(path, 'r')), content_type=guess_type(upload.original_filename)[0])
        response['Content-Disposition'] = 'attachment; filename=%s' % upload.original_filename
        response['Content-Length'] = upload.size

        return response

