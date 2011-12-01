#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.resources import Resource
from tastypie.utils.urls import trailing_slash

from redd import solr
from redd.api.datasets import DatasetResource
from redd.api.utils import CustomApiKeyAuthentication, CustomPaginator, CustomSerializer
from redd.models import Dataset

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

    def __str__(self):
        return str(self.__dict__['_data'])

    def __unicode__(self):
        return unicode(self.__dict__['_data'])

    def to_dict(self):
        return self._data

class DataResource(Resource):
    """
    API resource for row data.

    TKTK: implement write API
    """
    id = fields.CharField(attribute='id',
        help_text='Unique id of this row of data.')
    dataset_id = fields.IntegerField(attribute='dataset_id',
        help_text='Unique id of the dataset this row of data belongs to.')
    row = fields.IntegerField(attribute='row',
        help_text='Row number of this data in the source dataset.')
    data = fields.CharField(attribute='data',
        help_text='An ordered list of values corresponding to the columns in the parent dataset.')

    class Meta:
        resource_name = 'data'
        allowed_methods = ['get']

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()

    def dehydrate_data(self, bundle):
        """
        Convert csv data into a proper array for JSON serialization
        """
        return json.loads(bundle.data['data'])

    def dehydrate(self, bundle):
        """
        Trim the dataset_id field and add a proper relationship.

        TKTK -- better way to do this?
        """
        from redd.api.datasets import DatasetResource

        dataset = Dataset.objects.get(id=bundle.data['dataset_id'])
        dr = DatasetResource()
        uri = dr.get_resource_uri(dataset)

        del bundle.data['dataset_id']
        bundle.data['dataset'] = uri

        return bundle

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
        response = solr.query(settings.SOLR_DATA_CORE, '*:*')

        return [SolrObject(d) for d in response['response']['docs']]

    def obj_get_list(self, request=None, **kwargs):
        """
        TKTK: enforce proper limits from tastypie in solr query
        TKTK: How is this different from get_object_list?
        """
        response = solr.query(settings.SOLR_DATA_CORE, '*:*')

        return [SolrObject(d) for d in response['response']['docs']]

    def obj_get(self, request=None, **kwargs):
        """
        Query Solr for a single item by primary key.
        """
        if 'pk' in kwargs:
            get_id = kwargs['pk']
        else:
            get_id = request.GET.get('id', '')

        obj = solr.query(settings.SOLR_DATA_CORE, 'id:%s' % get_id)

        return SolrObject(obj['response']['docs'][0])

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/search%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('search'), name='api_search'),
        ]

    def search(self, request, **kwargs):
        """
        An endpoint for performing full-text searches.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        query = request.GET.get('q')
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_GROUPS))
        offset = int(request.GET.get('offset', 0))
        group_limit = int(request.GET.get('group_limit', settings.PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP))
        group_offset = int(request.GET.get('group_offset', 0))

        response = solr.query_grouped(
            settings.SOLR_DATA_CORE,
            query,
            'dataset_id',
            offset=offset,
            limit=limit,
            group_limit=group_limit,
            group_offset=group_offset
        )
        groups = response['grouped']['dataset_id']['groups']

        page = CustomPaginator(
            request.GET,
            groups,
            resource_uri=request.path_info,
            count=response['grouped']['dataset_id']['ngroups']
        ).page()

        datasets = []

        for group in groups:
            dataset_id = group['groupValue']
            results = group['doclist']

            dataset_search_url = reverse('api_search_dataset', kwargs={'api_name': kwargs['api_name'], 'resource_name': 'dataset', 'pk': dataset_id })

            dataset_resource = DatasetResource()
            dataset = Dataset.objects.get(id=dataset_id)
            dataset_bundle = dataset_resource.build_bundle(obj=dataset, request=request)
            dataset_bundle = dataset_resource.full_dehydrate(dataset_bundle)
            dataset_bundle = dataset_resource.simplify_bundle(dataset_bundle)

            objects = [SolrObject(obj) for obj in results['docs']]

            data_page = CustomPaginator(
                { 'limit': str(group_limit), 'offset': str(group_offset), 'q': query },
                objects,
                resource_uri=dataset_search_url,
                count=results['numFound']
            ).page()

            dataset_bundle.data.update(data_page)
            dataset_bundle.data['objects'] = []

            for obj in objects:
                data_bundle = self.build_bundle(obj=obj, request=request)
                data_bundle = self.full_dehydrate(data_bundle)
                dataset_bundle.data['objects'].append(data_bundle)

            datasets.append(dataset_bundle.data)

        page['objects'] = datasets

        self.log_throttled_access(request)

        return self.create_response(request, page)

    def search_dataset(self, request, **kwargs):
        """
        Perform a full-text search on only one dataset.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'pk' in kwargs:
            dataset_id = kwargs['pk']
        else:
            dataset_id = request.GET.get('id')

        dataset = Dataset.objects.get(id=dataset_id)

        query = request.GET.get('q')
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_ROWS))
        offset = int(request.GET.get('offset', 0))

        response = solr.query(
            settings.SOLR_DATA_CORE,
            'dataset_id:%s %s' % (dataset_id, query),
            offset=offset,
            limit=limit
        )

        dataset_resource = DatasetResource()
        dataset_bundle = dataset_resource.build_bundle(obj=dataset, request=request)
        dataset_bundle = dataset_resource.full_dehydrate(dataset_bundle)
        dataset_bundle = dataset_resource.simplify_bundle(dataset_bundle)
       
        results = [SolrObject(d) for d in response['response']['docs']]

        page = CustomPaginator(
            request.GET,
            results,
            resource_uri=request.path_info,
            count=response['response']['numFound']
        ).page() 
        
        dataset_bundle.data.update(page)
        dataset_bundle.data['objects'] = []

        for obj in results:
            bundle = self.build_bundle(obj=obj, request=request)
            bundle = self.full_dehydrate(bundle)
            dataset_bundle.data['objects'].append(bundle.data)

        self.log_throttled_access(request)

        return self.create_response(request, dataset_bundle)

