#!/usr/bin/env python

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.resources import Resource
from tastypie.validation import Validation

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

class DataValidation(Validation):
    """
    Tastypie Validation for Data objects.

    Unfortunatnely, since Tastypie does not pass **kwargs to the
    validation, this object is used manually by DataResource's
    write/update endpoints.
    """
    def is_valid(self, bundle, dataset_slug):
        errors = {}

        if 'data' not in bundle.data or not bundle.data['data']:
            errors['data'] = ['This field is required.']
            return errors
        
        dataset = Dataset.objects.get(slug=dataset_slug)

        field_count = len(bundle.data['data'])
        expected_field_count = len(dataset.schema)

        if field_count != expected_field_count:
            errors['data'] = ['Got %i data fields. Expected %i.' % (field_count, expected_field_count)]

        return errors

class DataResource(Resource):
    """
    API resource for row data.
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

    def get_object_list():
        """
        Intentionally not implemented. Should never be invoked.
        Endpoints handle their own object retrieval.
        """
        raise NotImplementedError() 

    def obj_get(self, request=None, **kwargs):
        """
        Query Solr for a single item by primary key.
        """
        if 'pk' in kwargs:
            get_id = kwargs['pk']
        else:
            get_id = request.GET.get('id', '')

        obj = solr.query(settings.SOLR_DATA_CORE, 'id:%s' % get_id)

        if len(obj['response']['docs']) < 1:
            raise ObjectDoesNotExist()

        if len(obj['response']['docs']) > 1:
            raise MultipleObjectsReturned()

        return SolrObject(obj['response']['docs'][0])

    def obj_get_list(self, request=None, **kwargs):
        """
        Intentionally not implemented. Should never be invoked.
        
        See get_list().
        """
        raise NotImplementedError() 

    def get_list(self, request, **kwargs):
        """
        List endpoint using Solr. Provides full-text search via the "q" parameter."

        We override get_list() rather than obj_get_list() since the Data objects
        are wrapped in Datasets.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        query = request.GET.get('q', '')
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

            dataset_resource = DatasetResource()
            dataset = Dataset.objects.get(id=dataset_id)
            dataset_bundle = dataset_resource.build_bundle(obj=dataset, request=request)
            dataset_bundle = dataset_resource.full_dehydrate(dataset_bundle)
            dataset_bundle = dataset_resource.simplify_bundle(dataset_bundle)

            objects = [SolrObject(obj) for obj in results['docs']]
            
            dataset_search_url = reverse('api_search_dataset', kwargs={'api_name': kwargs['api_name'], 'resource_name': 'dataset', 'slug': dataset.slug })

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

    def obj_create(self, bundle, request=None, **kwargs):
        """
        TODO
        """
        pass

    def obj_update(self, bundle, request=None, **kwargs):
        """
        TODO
        """
        pass

    def obj_delete(self, request=None, **kwargs):
        """
        TODO
        """
        pass

    def obj_delete_list(self, request=None, **kwargs):
        """
        TODO
        """
        pass

    def search_dataset(self, request, **kwargs):
        """
        Perform a full-text search on only one dataset.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'slug' in kwargs:
            slug = kwargs['slug']
        else:
            slug = request.GET.get('slug')

        dataset = Dataset.objects.get(slug=slug)

        query = request.GET.get('q')
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_ROWS))
        offset = int(request.GET.get('offset', 0))

        response = solr.query(
            settings.SOLR_DATA_CORE,
            'dataset_id:%s %s' % (dataset.id, query),
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

