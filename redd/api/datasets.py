#!/usr/bin/env python

from django.conf import settings
from django.conf.urls.defaults import url
from tastypie import fields
from tastypie import http
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils.mime import build_content_type
from tastypie.utils.urls import trailing_slash
from tastypie.validation import Validation

from redd import solr
from redd.api.utils import CustomApiKeyAuthentication, CustomPaginator, JSONApiField, SlugResource, CustomSerializer
from redd.models import Category, Dataset

class DatasetValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'name' not in bundle.data or not bundle.data['name']:
            errors['name'] = ['This field is required.']

        return errors

class DatasetResource(SlugResource):
    """
    API resource for Datasets.
    """
    from redd.api.category import CategoryResource
    from redd.api.tasks import TaskResource
    from redd.api.uploads import UploadResource
    from redd.api.users import UserResource

    categories = fields.ToManyField(CategoryResource, 'categories', full=True, null=True)
    creator = fields.ForeignKey(UserResource, 'creator', full=True, readonly=True)
    current_task = fields.ToOneField(TaskResource, 'current_task', full=True, null=True, readonly=True)
    data_upload = fields.ForeignKey(UploadResource, 'data_upload', full=True, null=True)

    # Read only fields
    slug = fields.CharField(attribute='slug', readonly=True)
    has_data = fields.BooleanField(attribute='has_data', readonly=True)
    sample_data = JSONApiField(attribute='sample_data', readonly=True, null=True)
    dialect = JSONApiField(attribute='dialect', readonly=True, null=True)
    row_count = fields.IntegerField(attribute='row_count', readonly=True, null=True)
    creation_date = fields.DateTimeField(attribute='creation_date', readonly=True)
    modified = fields.BooleanField(attribute='modified', readonly=True)

    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'dataset'
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        validation = DatasetValidation()
        serializer = CustomSerializer()

    def simplify_bundle(self, bundle):
        """
        Takes a dehydrated bundle and removes attributes to create a "simple"
        view that is faster over the wire.
        """
        del bundle.data['data_upload']
        del bundle.data['sample_data']
        del bundle.data['current_task']
        del bundle.data['dialect']

        return bundle

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        from redd.api.data import DataResource
        
        data_resource = DataResource(api_name=self._meta.api_name)

        return [
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r'^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)/import%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('import_data'), name='api_import_data'),
            
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
        query = request.GET.get('q', '')
        simple = True if request.GET.get('simple', 'false').lower() == 'true' else False

        if category_slug:
            category = Category.objects.get(slug=category_slug)
        else:
            category = None

        if category and query:
            q = 'categories:%s %s' % (category.id, query)
        elif category:
            q = 'categories:%s' % category.id
        else:
            q = query

        # TODO: fix sort
        response = solr.query(settings.SOLR_DATASETS_CORE, q, offset=offset, limit=limit, sort='slug desc')
        dataset_slugs = [d['slug'] for d in response['response']['docs']]

        datasets = Dataset.objects.filter(slug__in=dataset_slugs)

        paginator = CustomPaginator(request.GET, datasets, resource_uri=request.path_info, count=response['response']['numFound'])
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

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Set creating user on create.
        """
        return super(DatasetResource, self).obj_create(bundle, request=request, creator=request.user, **kwargs)

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

        errors = {}

        if not dataset.data_upload:
            errors['__all__'] = ['Can not import data for a dataset which does not have a data_upload set.']

        # Cribbed from is_valid()
        if errors:
            if request:
                desired_format = self.determine_format(request)
            else:
                desired_format = self._meta.default_format

            serialized = self.serialize(request, errors, desired_format)
            response = http.HttpBadRequest(content=serialized, content_type=build_content_type(desired_format))
            raise ImmediateHttpResponse(response=response)

        dataset.import_data()

        bundle = self.build_bundle(obj=dataset, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

