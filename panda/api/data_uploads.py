#!/usr/bin/env python

from mimetypes import guess_type

from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from tastypie import fields
from tastypie import http
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.utils.urls import trailing_slash

from panda.api.utils import JSONApiField, PandaAuthentication, PandaModelResource, PandaSerializer
from panda.exceptions import DataUploadNotDeletable
from panda.models import DataUpload

class DataUploadResource(PandaModelResource):
    """
    API resource for DataUploads.
    """
    from panda.api.users import UserResource

    filename = fields.CharField('filename', readonly=True)
    original_filename = fields.CharField('original_filename', readonly=True)
    size = fields.IntegerField('size', readonly=True)
    creator = fields.ForeignKey(UserResource, 'creator', full=True, readonly=True)
    creation_date = fields.DateTimeField('creation_date', readonly=True)
    title = fields.CharField('title', null=True)
    dataset = fields.ForeignKey('panda.api.datasets.DatasetResource', 'dataset', null=True, readonly=True)
    data_type = fields.CharField('data_type', null=True, readonly=True)
    encoding = fields.CharField('encoding', readonly=True)
    dialect = fields.CharField('dialect', null=True, readonly=True)
    columns = JSONApiField('columns', null=True, readonly=True)
    sample_data = JSONApiField('sample_data', null=True, readonly=True)
    guessed_types = JSONApiField('guessed_types', null=True, readonly=True)
    imported = fields.BooleanField('imported', readonly=True)

    class Meta:
        queryset = DataUpload.objects.all()
        resource_name = 'data_upload'
        allowed_methods = ['get', 'put', 'delete']
        always_return_data = True

        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('download'), name='api_download_data_upload'),
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
                raise NotFound(_("A model instance matching the provided arguments could not be found."))

        try:
            obj.delete()
        except DataUploadNotDeletable, e:
            raise ImmediateHttpResponse(response=http.HttpForbidden(e.message))

        if obj.dataset:
            obj.dataset.update_full_text()

    def download(self, request, **kwargs):
        """
        Download the original file that was uploaded.
        """
        # Allow POST so csrf token can come through
        self.method_check(request, allowed=['get', 'post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'pk' in kwargs:
            get_id = kwargs['pk']
        else:
            get_id = request.GET.get('id', '')

        upload = DataUpload.objects.get(id=get_id)
        path = upload.get_path()

        self.log_throttled_access(request)

        response = HttpResponse(FileWrapper(open(path, 'r')), content_type=guess_type(upload.original_filename)[0])
        response['Content-Disposition'] = 'attachment; filename=%s' % upload.original_filename
        response['Content-Length'] = upload.size

        return response

