#!/usr/bin/env python

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie.resources import Resource
from tastypie.utils.mime import build_content_type
from tastypie.validation import Validation

from redd import solr
from redd.api.datasets import DatasetResource
from redd.api.utils import CustomApiKeyAuthentication, CustomPaginator, CustomSerializer
from redd.models import Dataset
from redd.utils import make_row_data

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
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'data' not in bundle.data or not bundle.data['data']:
            errors['data'] = ['This field is required.']
            return errors

        return errors

class DataResource(Resource):
    """
    API resource for row data.
    """
    id = fields.CharField(attribute='id',
        help_text='Unique id of this row of data.')
    dataset_id = fields.IntegerField(attribute='dataset_id',
        help_text='Unique id of the dataset this row of data belongs to.')
    row = fields.IntegerField(attribute='row', null=True, blank=True,
        help_text='Row number of this data in the source dataset.')
    data = fields.CharField(attribute='data',
        help_text='An ordered list of values corresponding to the columns in the parent dataset.')

    class Meta:
        resource_name = 'data'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()
        validation = DataValidation()

        object_class = SolrObject

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
        get_id = kwargs['pk']
        
        try:
            slug = kwargs['dataset_slug']
            dataset = Dataset.objects.get(slug=slug)
            dataset_id = unicode(dataset.id)
        except KeyError:
            dataset_id = '*'

        obj = solr.query(settings.SOLR_DATA_CORE, 'id:%s dataset_id:%s' % (get_id, dataset_id))

        if len(obj['response']['docs']) < 1:
            raise NotFound()

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
        Retrieve a list of Data objects, optionally applying full-text search.

        Because these objects are sometimes wrapped in Datasets we override
        this instead of obj_get_list().
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        
        # Was this called from a url nested in a dataset?
        if 'dataset_slug' in kwargs:
            results = self.search_dataset_data(request, **kwargs)
        else:
            results = self.search_all_data(request)

        self.log_throttled_access(request)

        return self.create_response(request, results)

    def get_dataset_from_bundle_request_or_kwargs(self, bundle, request=None, **kwargs):
        """
        Extract a dataset from one of the variety of places it might be hiding.
        """
        bundle_uri = bundle.data.pop('dataset', None)
        kwargs_slug = kwargs.pop('dataset_slug', None)

        bundle_dataset = None
        kwargs_dataset = None

        if bundle_uri:
            bundle_dataset = DatasetResource().get_via_uri(bundle_uri)

        if kwargs_slug:
            kwargs_dataset = Dataset.objects.get(slug=kwargs_slug)

        if not bundle_dataset and not kwargs_dataset:
            raise BadRequest('When creating or updating Data you must specify a Dataset either by using a /api/x.y/dataset/[slug]/data/ endpoint or by providing a dataset uri in the body of the document.')

        if bundle_dataset and kwargs_dataset:
            if bundle_dataset.id != kwargs_dataset.id:
                raise BadRequest('Dataset specified in request body does not agree with dataset API endpoint used.')

        return bundle_dataset or kwargs_dataset

    def validate_bundle_data(self, bundle, request, dataset):
        """
        Perform additional validation that isn't possible with the Validation object.
        """
        errors = {}

        field_count = len(bundle.data['data'])
        expected_field_count = len(dataset.schema)

        if field_count != expected_field_count:
            errors['data'] = ['Got %i data fields. Expected %i.' % (field_count, expected_field_count)]

        # Cribbed from is_valid()
        if errors:
            if request:
                desired_format = self.determine_format(request)
            else:
                desired_format = self._meta.default_format

            serialized = self.serialize(request, errors, desired_format)
            response = http.HttpBadRequest(content=serialized, content_type=build_content_type(desired_format))
            raise ImmediateHttpResponse(response=response)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Add Data to a Dataset.

        TODO: committing everytime this is called doesn't make sense, especially
        since this function is called multiple times in put_list().
        """
        dataset = self.get_dataset_from_bundle_request_or_kwargs(bundle, request, **kwargs)

        self.validate_bundle_data(bundle, request, dataset)

        if 'row' in bundle.data:
            row = bundle.data['row']
        else:
            row = None

        data = make_row_data(dataset, bundle.data['data'], row)

        solr.add(settings.SOLR_DATA_CORE, [data], commit=True)

        dataset.row_count += 1
        dataset.save()

        bundle.obj = SolrObject(data)

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        Update an existing Data.
        """
        dataset = self.get_dataset_from_bundle_request_or_kwargs(bundle, request, **kwargs)
        
        if 'dataset_slug' in kwargs:
            del kwargs['dataset_slug']

        # Verify it exists
        data = self.obj_get(request, dataset_slug=dataset.slug, **kwargs)
        
        self.validate_bundle_data(bundle, request, dataset)

        if 'row' in bundle.data:
            row = bundle.data['row']
        else:
            row = None

        data = make_row_data(dataset, bundle.data['data'], row, kwargs['pk'])

        # Overwrite primary key
        solr.add(settings.SOLR_DATA_CORE, [data], commit=True)
        
        bundle.obj = SolrObject(data)

        return bundle

    def obj_delete(self, request=None, **kwargs):
        """
        TODO
        """
        pass

    def obj_delete_list(self, request=None, **kwargs):
        """
        Don't support disabling entire collection. Will also implicitly disable
        put_list().
        """
        raise NotImplementedError() 

    def search_all_data(self, request, **kwargs):
        """
        List endpoint using Solr. Provides full-text search via the "q" parameter."

        We override get_list() rather than obj_get_list() since the Data objects
        are wrapped in Datasets.
        """
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
            
            dataset_search_url = reverse('api_dataset_data_list', kwargs={ 'api_name': self._meta.api_name, 'dataset_resource_name': 'dataset', 'resource_name': 'data', 'dataset_slug': dataset.slug })

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

        return page

    def search_dataset_data(self, request, **kwargs):
        """
        Perform a full-text search on only one dataset.
        """
        dataset = Dataset.objects.get(slug=kwargs['dataset_slug'])

        query = request.GET.get('q', '')
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

        return dataset_bundle

