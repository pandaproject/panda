#!/usr/bin/env python

from copy import copy

from django.conf.urls.defaults import url
from sunburnt import SolrInterface
from sunburnt.search import SolrSearch
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource, Resource
from tastypie.utils.urls import trailing_slash

from redd.models import Dataset, Upload

class UploadResource(ModelResource):
    """
    API resource for Uploads.

    TKTK: must be read-only.
    """
    class Meta:
        queryset = Upload.objects.all()
        resource_name = 'upload'

        # TKTK
        authentication = Authentication()
        authorization = Authorization()

class DatasetResource(ModelResource):
    """
    API resource for Datasets.
    """
    data_upload = fields.ForeignKey(UploadResource, 'data_upload')

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'dataset'

        # TKTK
        authentication = Authentication()
        authorization = Authorization()

class SolrObject(object):
    """
    A lightweight wrapper around a Solr response object for use when
    querying Solr via Tastypie.
    """
    def __init__(self, initial=None, **kwargs):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

        self.__dict__['_data'].update(kwargs)

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data

class DataResource(Resource):
    """
    API resource for row data.
    """
    # TKTK - handle other fields
    id = fields.CharField(attribute='id')
    dataset_id = fields.CharField(attribute='dataset_id')

    class Meta:
        resource_name = 'data'

    def _solr(self):
        """
        Create a query interface for Solr.
        """
        return SolrInterface('http://localhost:8983/solr')

    def get_resource_uri(self, bundle_or_obj):
        """
        Build a canonical uri for a datum.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request):
        """
        Get all objects.

        TKTK: enforce proper limits from tastypie in solr query
        """
        s = SolrSearch(self._solr())

        return s.execute(constructor=SolrObject)

    def obj_get_list(self, request=None, **kwargs):
        """
        Query Solr with a list of terms.
        """
        q = copy(request.GET)
        # TKTK - what other params need to be ignored?
        del q['format']

        s = SolrSearch(self._solr()).query(**q)

        return s.execute(constructor=SolrObject)

    def obj_get(self, request=None, **kwargs):
        """
        Query Solr for a single item by primary key.
        """
        if 'pk' in kwargs:
            get_id = kwargs['pk']
        else:
            get_id = request.GET.get('id', '')

        obj = self._solr().query(id=get_id).execute(constructor=SolrObject)

        return SolrObject(obj)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        TKTK
        """
        pass

    def obj_update(self, bundle, request=None, **kwargs):
        """
        TKTK
        """
        pass

    def obj_delete_list(self, request=None, **kwargs):
        """
        TKTK
        """
        pass

    def obj_delete(self, request=None, **kwargs):
        """
        TKTK
        """
        pass

    def rollback(self, bundles):
        """
        TKTK
        """
        pass

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/search%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('search'), name='api_search'),
        ]

    def search(self, request, **kwargs):
        """
        TKTK
        """
        pass
