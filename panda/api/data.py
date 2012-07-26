#!/usr/bin/env python

import re

from django.conf import settings
from django.conf.urls.defaults import url
from django.core.urlresolvers import get_script_prefix, resolve, reverse
from django.utils import simplejson as json
from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie.utils import dict_strip_unicode_keys 
from tastypie.utils.mime import build_content_type
from tastypie.utils.urls import trailing_slash
from tastypie.validation import Validation

from panda import solr
from panda.api.datasets import DatasetResource
from panda.exceptions import DatasetLockedError
from panda.api.utils import PandaApiKeyAuthentication, PandaPaginator, PandaResource, PandaSerializer
from panda.models import Category, Dataset, SearchLog, TaskStatus
from panda.tasks import ExportSearchTask, PurgeDataTask

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
            errors['data'] = ['The data field is required.']

        if 'external_id' in bundle.data:
            if not isinstance(bundle.data['external_id'], basestring):
                errors['external_id'] = ['external_id must be a string.']
            elif not re.match('^[\w\d_-]+$', bundle.data['external_id']):
                errors['external_id'] = ['external_id can only contain letters, numbers, underscores and dashes.']

        return errors

class DataResource(PandaResource):
    """
    API resource for data.
    """
    dataset_slug = fields.CharField(attribute='dataset_slug',
        help_text='Slug of the dataset this row of data belongs to.')
    external_id = fields.CharField(attribute='external_id', null=True, blank=True,
        help_text='Per-dataset unique identifier for this row of data.')
    data = fields.CharField(attribute='data',
        help_text='An ordered list of values corresponding to the columns in the parent dataset.')

    class Meta:
        resource_name = 'data'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()
        validation = DataValidation()

        object_class = SolrObject

    def override_urls(self):
        """
        Add urls for export.
        """
        url(r'^export%s' % trailing_slash(), self.wrap_view('search_export'), name='api_data_search_export'),

    def dehydrate_data(self, bundle):
        """
        Convert csv data into a proper array for JSON serialization
        """
        return json.loads(bundle.data['data'])

    def dehydrate(self, bundle):
        """
        Trim the dataset_slug field and add a proper relationship.
        """
        dataset = Dataset.objects.get(slug=bundle.data['dataset_slug'])

        del bundle.data['dataset_slug']
        bundle.data['dataset'] = DatasetResource().get_resource_uri(dataset)

        return bundle

    def get_resource_uri(self, bundle_or_obj):
        """
        Build a canonical uri for a datum.

        If the resource doesn't have an external_id it is
        considered "unaddressable" and this will return None.
        """
        dr = DatasetResource()

        kwargs = {
            'api_name': self._meta.api_name,
            'dataset_resource_name': dr._meta.resource_name,
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['dataset_slug'] = bundle_or_obj.obj.dataset_slug
            kwargs['external_id'] = bundle_or_obj.obj.external_id
        else:
            kwargs['dataset_slug'] = bundle_or_obj.dataset_slug
            kwargs['external_id'] = bundle_or_obj.external_id
 
        if not kwargs['external_id']:
            return None

        return dr._build_reverse_url('api_dataset_data_detail', kwargs=kwargs)

    def get_dataset_from_kwargs(self, bundle, **kwargs):
        """
        Extract a dataset from one of the variety of places it might be hiding.
        """
        kwargs_slug = kwargs['dataset_slug']
        
        bundle_uri = None
        bundle_slug = None

        if bundle:
            bundle_uri = bundle.data.pop('dataset', None)

        if bundle_uri:
            prefix = get_script_prefix()

            if prefix and bundle_uri.startswith(prefix):
                bundle_uri = bundle_uri[len(prefix)-1:]

            view, args, kwargs = resolve(bundle_uri)

            bundle_slug = kwargs['slug']

        if bundle_slug and bundle_slug != kwargs_slug:
            raise BadRequest('Dataset specified in request body does not agree with dataset API endpoint used.')

        return Dataset.objects.get(slug=kwargs_slug) 

    def validate_bundle_data(self, bundle, request, dataset):
        """
        Perform additional validation that isn't possible with the Validation object.
        """
        errors = {}

        field_count = len(bundle.data['data'])

        if dataset.initial_upload and not dataset.row_count:
            errors['dataset'] = ['Can not create or modify data for a dataset which has initial_upload, but has not completed the import process.']

        if dataset.column_schema is None:
            errors['dataset'] = ['Can not create or modify data for a dataset without columns.']
        else:
            expected_field_count = len(dataset.column_schema)

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

    # Data access methods

    def get_object_list():
        """
        Bypassed, should never be invoked. 

        Since Solr queries are not lazy, fetching a complete list
        of objects never makes sense.
        """
        raise NotImplementedError() 

    def obj_get_list(self, request=None, **kwargs):
        """
        Bypassed, should never be invoked. 
        
        See ``get_list``.
        """
        raise NotImplementedError() 

    def obj_get(self, request=None, **kwargs):
        """
        Query Solr for a single item by primary key.
        """
        dataset = Dataset.objects.get(slug=kwargs['dataset_slug'])

        row = dataset.get_row(kwargs['external_id'])

        if not row:
            raise NotFound()

        return SolrObject(row)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Add one Data to a Dataset.
        """
        dataset = self.get_dataset_from_kwargs(bundle, **kwargs)

        self.validate_bundle_data(bundle, request, dataset)

        if 'external_id' in bundle.data:
            external_id = bundle.data['external_id']
        elif 'external_id' in kwargs:
            external_id = kwargs['external_id']
        else:
            external_id = None

        try:
            row = dataset.add_row(request.user, bundle.data['data'], external_id=external_id)
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden('Dataset is currently locked by another process.'))

        bundle.obj = SolrObject(row)

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        Overwrite an existing Data.
        """
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete_list(self, request=None, **kwargs):
        """
        See ``put_list``. 
        """
        raise NotImplementedError()

    def obj_delete(self, request=None, **kwargs):
        """
        Delete a ``Data``.
        """
        dataset = Dataset.objects.get(slug=kwargs['dataset_slug'])

        try:
            dataset.delete_row(request.user, kwargs['external_id'])
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden('Dataset is currently locked by another process.'))

    def rollback(self, bundles):
        """
        See ``put_list``.
        """
        raise NotImplementedError()

    # Views

    def get_list(self, request, **kwargs):
        """
        Retrieve a list of ``Data`` objects, optionally applying full-text search.

        Bypasses ``obj_get_list``, making it unnecessary.
        """
        results = self.search_dataset_data(request, **kwargs)

        return self.create_response(request, results)

    def get_detail(self, request, **kwargs):
        """
        Handled by the underlying implementation.

        See ``obj_get``.
        """
        return super(DataResource, self).get_detail(request, **kwargs)

    def put_list(self, request, **kwargs):
        """
        A custom bulk create/update handler. Notes: 

        * ``obj_delete_list`` is never called, objects are overwritten instead.
        * All objects are validated before any objects are created, so ``rollback`` is unnecessary.
        * A single dataset save and Solr commit are made at the end (optimization!).
        """
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)

        if not 'objects' in deserialized:
            raise BadRequest("Invalid data sent.")

        bundles = []
        data = []

        dataset = self.get_dataset_from_kwargs(None, **kwargs)

        for object_data in deserialized['objects']:
            bundle = self.build_bundle(data=dict_strip_unicode_keys(object_data), request=request)

            self.is_valid(bundle, request)

            if bundle.errors:
                self.error_response(bundle.errors, request)

            bundles.append(bundle)
            data.append((
                bundle.data['data'],
                bundle.data.get('external_id', None) 
            ))
        
            self.validate_bundle_data(bundle, request, dataset)
        
        try:
            solr_rows = dataset.add_many_rows(request.user, data)
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden('Dataset is currently locked by another process.'))

        for bundle, solr_row in zip(bundles, solr_rows):
            bundle.obj = SolrObject(solr_row)

        if not self._meta.always_return_data:
            return http.HttpNoContent()
        else:
            to_be_serialized = {}
            to_be_serialized['objects'] = [self.full_dehydrate(bundle) for bundle in bundles]
            to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

            return self.create_response(request, to_be_serialized, response_class=http.HttpAccepted)

    def put_detail(self, request, **kwargs):
        """
        Handled by the underlying implementation.

        See ``obj_update``.
        """
        return super(DataResource, self).put_detail(request, **kwargs)

    def post_list(self, request, **kwargs):
        """
        Handled by the underlying implementation.

        See ``obj_create``.
        """
        return super(DataResource, self).post_list(request, **kwargs)

    def post_detail(self, request, **kwargs):
        """
        Handled by the underlying implementation, which means this is
        not supported.
        """
        return super(DataResource, self).post_detail(request, **kwargs)

    def delete_list(self, request, **kwargs):
        """
        Delete all ``Data`` in a ``Dataset``. Must be called from a data
        url nested under a Dataset. Deleting *all* ``Data`` objects is
        not supported.
        """
        dataset = Dataset.objects.get(slug=kwargs['dataset_slug'])
        
        try:
            dataset.delete_all_rows(request.user) 
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden('Dataset is currently locked by another process.'))

        return http.HttpNoContent()

    def delete_detail(self, request, **kwargs):
        return super(DataResource, self).delete_detail(request, **kwargs)

    # Search

    def search_all_data(self, request, **kwargs):
        """
        List endpoint using Solr. Provides full-text search via the "q" parameter."
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        since = request.GET.get('since', None)
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_GROUPS))
        offset = int(request.GET.get('offset', 0))
        group_limit = int(request.GET.get('group_limit', settings.PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP))
        group_offset = int(request.GET.get('group_offset', 0))

        if category:
            if category != 'uncategorized':
                category = Category.objects.get(slug=category)
                dataset_slugs = category.datasets.values_list('slug', flat=True)
            else:
                dataset_slugs = Dataset.objects.filter(categories=None).values_list('slug', flat=True) 

            query += ' dataset_slug:(%s)' % ' '.join(dataset_slugs)

        if since:
            query = 'last_modified:[' + since + 'Z TO *] AND (%s)' % query

        response = solr.query_grouped(
            settings.SOLR_DATA_CORE,
            query,
            'dataset_slug',
            offset=offset,
            limit=limit,
            group_limit=group_limit,
            group_offset=group_offset
        )
        groups = response['grouped']['dataset_slug']['groups']

        page = PandaPaginator(
            request.GET,
            groups,
            resource_uri=request.path_info,
            count=response['grouped']['dataset_slug']['ngroups']
        ).page()

        datasets = []

        for group in groups:
            dataset_slug = group['groupValue']
            results = group['doclist']
            
            try:
                dataset = Dataset.objects.get(slug=dataset_slug)
            # In the event that stale data exists in Solr, skip this dataset,
            # request the invalid data be purged and return the other results.
            # Pagination may be wrong, but this is the most functional solution. (#793)
            except Dataset.DoesNotExist:
                PurgeDataTask.apply_async(args=[dataset_slug])
                solr.delete(settings.SOLR_DATASETS_CORE, 'slug:%s' % dataset_slug)

                page['meta']['total_count'] -= 1

                continue
            
            dataset_resource = DatasetResource()
            dataset_bundle = dataset_resource.build_bundle(obj=dataset, request=request)
            dataset_bundle = dataset_resource.full_dehydrate(dataset_bundle)
            dataset_bundle = dataset_resource.simplify_bundle(dataset_bundle)

            objects = [SolrObject(obj) for obj in results['docs']]
            
            dataset_search_url = reverse('api_dataset_data_list', kwargs={ 'api_name': self._meta.api_name, 'dataset_resource_name': 'dataset', 'resource_name': 'data', 'dataset_slug': dataset.slug })

            data_page = PandaPaginator(
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
        
        # Log query
        SearchLog.objects.create(user=request.user, dataset=None, query=query)

        self.log_throttled_access(request)

        return self.create_response(request, page)

    def search_export(self, request, **kwargs):
        """
        Export the results of a Solr query.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        since = request.GET.get('since', None)

        if category:
            if category != 'uncategorized':
                category = Category.objects.get(slug=category)
                dataset_slugs = category.datasets.values_list('slug', flat=True)
            else:
                dataset_slugs = Dataset.objects.filter(categories=None).values_list('slug', flat=True) 

            query += ' dataset_slug:(%s)' % ' '.join(dataset_slugs)

        if since:
            query = 'last_modified:[' + since + 'Z TO *] AND (%s)' % query

        task_type = ExportSearchTask

        task = TaskStatus.objects.create(
            task_name=task_type.name,
            task_description='Export search results for "%s".' % query,
            creator=request.user
        )

        task_type.apply_async(
            args=[query, task.id],
            kwargs={},
            task_id=task.id
        )

        self.log_throttled_access(request)

        return self.create_response(request, 'Export queued.')

    def search_dataset_data(self, request, **kwargs):
        """
        Perform a full-text search on only one dataset.

        See ``get_list``.
        """
        dataset = Dataset.objects.get(slug=kwargs['dataset_slug'])

        query = request.GET.get('q', '')
        since = request.GET.get('since', None)
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_ROWS))
        offset = int(request.GET.get('offset', 0))

        if query:
            solr_query = 'dataset_slug:%s AND (%s)' % (dataset.slug, query)
        else:
            solr_query = 'dataset_slug:%s' % dataset.slug

        if since:
            solr_query += ' AND last_modified:[' + since + 'Z TO *]'

        response = solr.query(
            settings.SOLR_DATA_CORE,
            solr_query,
            offset=offset,
            limit=limit
        )

        dataset_resource = DatasetResource()
        dataset_bundle = dataset_resource.build_bundle(obj=dataset, request=request)
        dataset_bundle = dataset_resource.full_dehydrate(dataset_bundle)
        dataset_bundle = dataset_resource.simplify_bundle(dataset_bundle)
       
        results = [SolrObject(d) for d in response['response']['docs']]

        page = PandaPaginator(
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
        
        SearchLog.objects.create(user=request.user, dataset=dataset, query=query)

        return dataset_bundle

