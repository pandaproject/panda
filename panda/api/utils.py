#!/usr/bin/env python

from urllib import unquote

from django.conf import settings
from django.conf.urls.defaults import url
from django.http import HttpResponse
from django.middleware.csrf import _sanitize_token, constant_time_compare
from django.utils.http import same_origin
from tastypie.authentication import ApiKeyAuthentication
from tastypie.bundle import Bundle
from tastypie.fields import ApiField, CharField
from tastypie.paginator import Paginator
from tastypie.resources import ModelResource, Resource
from tastypie.serializers import Serializer
from tastypie.utils.urls import trailing_slash

from panda.fields import JSONField
from panda.models import UserProxy

PANDA_CACHE_CONTROL = 'max-age=0,no-cache,no-store'

class JSONApiField(ApiField):
    """
    Custom ApiField for dealing with data from custom JSONFields.
    """
    dehydrated_type = 'json'
    help_text = 'JSON structured data.'
    
    def dehydrate(self, obj):
        return self.convert(super(JSONApiField, self).dehydrate(obj))
    
    def convert(self, value):
        if value is None:
            return None

        return value

class PandaResource(Resource):
    """
    Resource subclass that overrides cache headers.
    """
    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Override response generation to add ``Cache-Control: no-cache`` header.
        """
        response = super(PandaResource, self).create_response(request, data, response_class, **response_kwargs)
        response['Cache-Control'] = PANDA_CACHE_CONTROL

        return response

class PandaModelResource(ModelResource):
    """
    ModelResource subclass that supports JSONFields.
    """
    @classmethod
    def api_field_from_django_field(cls, f, default=CharField):
        """
        Overrides default field handling to support custom ListField and JSONField.
        """
        if isinstance(f, JSONField):
            return JSONApiField
    
        return super(PandaModelResource, cls).api_field_from_django_field(f, default)

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Override response generation to add ``Cache-Control: no-cache`` header.
        """
        response = super(PandaModelResource, self).create_response(request, data, response_class, **response_kwargs)
        response['Cache-Control'] = PANDA_CACHE_CONTROL

        return response

class SluggedModelResource(PandaModelResource):
    """
    ModelResource that uses slugs for URLs.

    Also supports JSONFields, for simplicity.
    """
    def get_resource_uri(self, bundle_or_obj):
        """
        Handles generating a resource URI for a single resource.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['slug'] = bundle_or_obj.obj.slug
        else:
            kwargs['slug'] = bundle_or_obj.slug

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<slug_list>[\w\d_-]+)/$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_-]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class PandaAuthentication(ApiKeyAuthentication):
    """
    Custom API Auth that authenticates via sessions, headers or querystring parameters. 
    """
    def try_sessions(self, request, **kwargs):
        """
        Attempt to authenticate with sessions.

        Cribbed from a newer version of Tastypie than we're using.
        """
        csrf_token = _sanitize_token(request.COOKIES.get(settings.CSRF_COOKIE_NAME, ''))

        if request.is_secure():
            referer = request.META.get('HTTP_REFERER')

            if referer is None:
                return False

            good_referer = 'https://%s/' % request.get_host()

            if not same_origin(referer, good_referer):
                return False

        # Tastypie docstring says accessing POST here isn't safe, but so far it's not causing any problems...
        # This is necessary for downloads that post the csrf token from an iframe
        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '') or request.POST.get('csrfmiddlewaretoken', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.user.is_authenticated()

    def try_api_keys(self, request, **kwargs):
        """
        Attempt to authenticate with API keys in headers or parameters.
        """
        email = request.META.get('HTTP_PANDA_EMAIL') or request.GET.get('email')
        api_key = request.META.get('HTTP_PANDA_API_KEY') or request.GET.get('api_key')

        if email:
            email = unquote(email)

        if not email or not api_key:
            return False

        try:
            user = UserProxy.objects.get(username=email.lower())
        except (UserProxy.DoesNotExist, UserProxy.MultipleObjectsReturned):
            return False 

        if not user.is_active:
            return False
        
        request.user = user

        return self.get_key(user, api_key)

    def is_authenticated(self, request, **kwargs):
        authenticated = self.try_sessions(request, **kwargs)

        if authenticated:
            return True

        authenticated = self.try_api_keys(request, **kwargs)

        if authenticated:
            return True

        return self._unauthorized()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """
        return request.user.username

class PandaSerializer(Serializer):
    """
    A custom serializer that truncates microseconds from iso8601.
    """
    def format_datetime(self, data):
        return data.strftime('%Y-%m-%dT%H:%M:%S')

class PandaPaginator(Paginator):
    """
    A customized paginator that accepts count as a property, rather
    then inferring it from the length of the object array.
    """
    def __init__(self, request_data, objects, resource_uri=None, limit=None, offset=0, count=None):
        self.count = count
        super(PandaPaginator, self).__init__(request_data, objects, resource_uri, limit, offset)

    def get_count(self):
        if self.count is not None:
            return self.count
        
        return super(PandaPaginator, self).get_count()

