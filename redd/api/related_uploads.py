#!/usr/bin/env python

from mimetypes import guess_type

from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import NotFound
from tastypie.utils.urls import trailing_slash

from redd.api.utils import PandaApiKeyAuthentication, PandaModelResource, PandaSerializer
from redd.models import RelatedUpload

class RelatedUploadResource(PandaModelResource):
    """
    API resource for DataUploads.
    """
    from redd.api.users import UserResource

    creator = fields.ForeignKey(UserResource, 'creator', full=True)
    dataset = fields.ForeignKey('redd.api.datasets.DatasetResource', 'dataset')

    class Meta:
        queryset = RelatedUpload.objects.all()
        resource_name = 'related_upload'
        allowed_methods = ['get', 'delete']

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('download'), name='api_download_related_upload'),
        ]

    def obj_delete(self, request=None, **kwargs):
        """
        Override delete to also update related Dataset's metadata.
        """
        obj = kwargs.pop('_obj', None)

        if not hasattr(obj, 'delete'):
            try:
                obj = self.obj_get(request, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        obj.delete()

        if obj.dataset:
            obj.dataset.update_full_text()

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

        upload = RelatedUpload.objects.get(id=get_id)
        path = upload.get_path()

        self.log_throttled_access(request)

        response = HttpResponse(FileWrapper(open(path, 'r')), content_type=guess_type(upload.original_filename)[0])
        response['Content-Disposition'] = 'attachment; filename=%s' % upload.original_filename
        response['Content-Length'] = upload.size

        return response

