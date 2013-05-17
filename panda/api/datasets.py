#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import url
from django.utils.translation import ugettext_lazy as _
from tastypie import fields
from tastypie import http
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.utils.urls import trailing_slash
from tastypie.validation import Validation

from panda import solr
from panda.api.utils import PandaAuthentication, PandaPaginator, JSONApiField, SluggedModelResource, PandaSerializer
from panda.exceptions import DataImportError, DatasetLockedError
from panda.models import Category, Dataset, DataUpload, UserProxy
from panda.utils.column_schema import make_column_schema

class DatasetValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'name' not in bundle.data or not bundle.data['name']:
            errors['name'] = [_('This field is required.')]

        return errors

class DatasetResource(SluggedModelResource):
    """
    API resource for Datasets.
    """
    from panda.api.category import CategoryResource
    from panda.api.tasks import TaskResource
    from panda.api.data_uploads import DataUploadResource
    from panda.api.users import UserResource

    categories = fields.ToManyField(CategoryResource, 'categories', full=True, null=True)
    creator = fields.ForeignKey(UserResource, 'creator', full=True, readonly=True)
    current_task = fields.ToOneField(TaskResource, 'current_task', full=True, null=True, readonly=True)
    related_uploads = fields.ToManyField('panda.api.related_uploads.RelatedUploadResource', 'related_uploads', full=True, null=True)
    data_uploads = fields.ToManyField('panda.api.data_uploads.DataUploadResource', 'data_uploads', full=True, null=True)
    last_modified_by = fields.ForeignKey(UserResource, 'last_modified_by', full=True, readonly=True, null=True)
    initial_upload = fields.ForeignKey(DataUploadResource, 'initial_upload', readonly=True, null=True)

    slug = fields.CharField(attribute='slug')
    column_schema = JSONApiField(attribute='column_schema', readonly=True, null=True)
    sample_data = JSONApiField(attribute='sample_data', readonly=True, null=True)
    row_count = fields.IntegerField(attribute='row_count', readonly=True, null=True)
    creation_date = fields.DateTimeField(attribute='creation_date', readonly=True, null=True)
    last_modified = fields.DateTimeField(attribute='last_modified', readonly=True, null=True)
    last_modification = fields.CharField(attribute='last_modification', readonly=True, null=True)
    last_modified_by = fields.ForeignKey(UserResource, 'last_modified_by', full=True, null=True, readonly=True)
    locked = fields.BooleanField(attribute='locked', readonly=True, null=True)
    locked_at = fields.DateTimeField(attribute='locked_at', readonly=True, null=True)

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'dataset'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True

        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        validation = DatasetValidation()
        serializer = PandaSerializer()

    def simplify_bundle(self, bundle):
        """
        Takes a dehydrated bundle and removes attributes to create a "simple"
        view that is faster over the wire.
        """
        del bundle.data['data_uploads']
        del bundle.data['related_uploads']
        del bundle.data['sample_data']
        del bundle.data['current_task']

        return bundle

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        from panda.api.data import DataResource
        
        data_resource = DataResource(api_name=self._meta.api_name)

        return [
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r'^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)/import/(?P<upload_id>\d+)%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('import_data'), name='api_import_data'),
            url(r'^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)/export%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('export_data'), name='api_export_data'),
            url(r'^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)/reindex%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('reindex_data'), name='api_reindex_data'),
            
            # Nested urls for accessing data
            url(r'^(?P<dataset_resource_name>%s)/(?P<dataset_slug>[\w\d_-]+)/(?P<resource_name>%s)%s$' % (self._meta.resource_name, data_resource._meta.resource_name, trailing_slash()), data_resource.wrap_view('dispatch_list'), name='api_dataset_data_list'),
            url(r'^(?P<dataset_resource_name>%s)/(?P<dataset_slug>[\w\d_-]+)/(?P<resource_name>%s)/(?P<external_id>[\w\d_-]+)%s$' % (self._meta.resource_name, data_resource._meta.resource_name, trailing_slash()), data_resource.wrap_view('dispatch_detail'), name='api_dataset_data_detail'),
            url(r'^data%s' % trailing_slash(), data_resource.wrap_view('search_all_data'), name='api_data_search')
        ]

    def get_list(self, request, **kwargs):
        """
        List endpoint using Solr. Provides full-text search via the "q" parameter."
        """
        limit = int(request.GET.get('limit', settings.PANDA_DEFAULT_SEARCH_ROWS))
        offset = int(request.GET.get('offset', 0))
        category_slug = request.GET.get('category', None)
        creator_email = request.GET.get('creator_email', None)
        query = request.GET.get('q', '')
        simple = True if request.GET.get('simple', 'false').lower() == 'true' else False

        if category_slug == settings.PANDA_UNCATEGORIZED_SLUG:
            category_id = settings.PANDA_UNCATEGORIZED_ID
        elif category_slug:
            category_id = Category.objects.get(slug=category_slug).id
        else:
            category_id = None

        if category_id is not None and query:
            q = 'categories:%s %s' % (category_id, query)
        elif category_id is not None:
            q = 'categories:%s' % category_id
        else:
            q = query

        if creator_email:
            datasets = Dataset.objects.filter(creator__email=creator_email)
            count = datasets.count()
            datasets = datasets[offset:offset + limit]
        else:
            response = solr.query(settings.SOLR_DATASETS_CORE, q, offset=offset, limit=limit, sort='creation_date desc')
            count = response['response']['numFound']
            
            dataset_slugs = [d['slug'] for d in response['response']['docs']]
            datasets = Dataset.objects.filter(slug__in=dataset_slugs)

        paginator = PandaPaginator(request.GET, datasets, resource_uri=request.path_info, count=count)
        page = paginator.page()

        objects = []

        for obj in datasets:
            bundle = self.build_bundle(obj=obj, request=request)
            bundle = self.full_dehydrate(bundle)

            # Prune attributes we don't care about
            if simple:
                bundle = self.simplify_bundle(bundle)

            objects.append(bundle)

        page['objects'] = objects

        return self.create_response(request, page)

    def put_detail(self, request, **kwargs):
        """
        Allow emulating a ``PATCH`` request by passing ``?patch=true``.
        (As a workaround for IE's broken XMLHttpRequest.)
        """
        if request.GET.get('patch', 'false').lower() == 'true':
            return super(DatasetResource, self).patch_detail(request, **kwargs)
        else:
            return super(DatasetResource, self).put_detail(request, **kwargs)

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Set creator and update full text.
        """
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        bundle = super(DatasetResource, self).obj_create(bundle, request=request, creator=user, **kwargs)

        if 'columns' in request.GET:
            columns = request.GET['columns'].split(',')
        else:
            columns = None

        if 'typed_columns' in request.GET:
            if not columns:
                raise BadRequest(_('The "columns" argument must also be specified when specifying "typed_columns".'))

            typed_columns = [True if c.lower() == 'true' else False for c in request.GET['typed_columns'].split(',')]

            if len(typed_columns) != len(columns):
                raise BadRequest(_('The "typed_columns" argument must be a comma-separated list of True/False values with the same number of values as the "columns" argument.'))
        else:
            typed_columns = None

        if 'column_types' in request.GET:
            if not columns:
                raise BadRequest(_('The "columns" argument must also be specified when specifying "column_types".'))

            column_types = [None if c.lower() == '' else c.lower() for c in request.GET['column_types'].split(',')]

            if len(column_types) != len(columns):
                raise BadRequest(_('The "column_types" argument must be a comma-separated list of types with the same number of values as the "columns" argument.'))
        else:
            column_types = None

        if columns:
            bundle.obj.column_schema = make_column_schema(columns, typed_columns, column_types)
            bundle.obj.save()

        # After ALL changes have been made to the object and its relations, update its full text in Solr.
        bundle.obj.update_full_text()

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        Update full text.
        """
        bundle = super(DatasetResource, self).obj_update(bundle, request=request, **kwargs)

        # After ALL changes have been made to the object and its relations, update its full text in Solr.
        bundle.obj.update_full_text()

        return bundle

    def import_data(self, request, **kwargs):
        """
        Dummy endpoint for kicking off data import tasks.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'slug' in kwargs:
            slug = kwargs['slug']
        else:
            slug = request.GET.get('slug')

        dataset = Dataset.objects.get(slug=slug)
        upload = DataUpload.objects.get(id=kwargs['upload_id'])

        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        try:
            dataset.import_data(user, upload)
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden(_('Dataset is currently locked by another process.')))
        except DataImportError, e:
            raise ImmediateHttpResponse(response=http.HttpForbidden(e.message))

        dataset.update_full_text()

        bundle = self.build_bundle(obj=dataset, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

    def reindex_data(self, request, **kwargs):
        """
        Dummy endpoint for kicking off data reindexing tasks.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'slug' in kwargs:
            slug = kwargs['slug']
        else:
            slug = request.GET.get('slug')

        dataset = Dataset.objects.get(slug=slug)

        if not dataset.column_schema:
            raise BadRequest(_('This dataset has no data to reindex.'))

        if 'typed_columns' in request.GET:
            typed_columns = [True if c.lower() == 'true' else False for c in request.GET['typed_columns'].split(',')]

            if len(typed_columns) != len(dataset.column_schema):
                raise BadRequest(_('typed_columns must be a comma-separated list of True/False values with the same number of values as the dataset has columns.'))
        else:
            typed_columns = None

        if 'column_types' in request.GET:
            column_types = [None if c.lower() == '' else c.lower() for c in request.GET['column_types'].split(',')]

            if len(column_types) != len(dataset.column_schema):
                raise BadRequest(_('column_types must be a comma-separated list of types with the same number of values as the dataset has columns.'))
        else:
            column_types = None

        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        try:
            dataset.reindex_data(user, typed_columns=typed_columns, column_types=column_types)
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden(_('Dataset is currently locked by another process.')))

        dataset.update_full_text()

        bundle = self.build_bundle(obj=dataset, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

    def export_data(self, request, **kwargs):
        """
        Dummy endpoint for kicking off data export tasks.

        NB: This endpoint is used for both exporting complete datasets
        (without a query arg) and exporting dataset search results
        (with a query arg).
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'slug' in kwargs:
            slug = kwargs['slug']
        else:
            slug = request.GET.get('slug')

        dataset = Dataset.objects.get(slug=slug)

        query = request.GET.get('q', '')
        since = request.GET.get('since', None)

        if since:
            query = 'last_modified:[' + since + 'Z TO *] AND (%s)' % query

        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        try:
            dataset.export_data(user, query=query)
        except DatasetLockedError:
            raise ImmediateHttpResponse(response=http.HttpForbidden(_('Dataset is currently locked by another process.')))

        bundle = self.build_bundle(obj=dataset, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

