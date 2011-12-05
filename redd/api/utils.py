#!/usr/bin/env python

from urllib import unquote

from django.conf.urls.defaults import url
from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication
from tastypie.bundle import Bundle
from tastypie.fields import ApiField, CharField
from tastypie.paginator import Paginator
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils.urls import trailing_slash

from redd.fields import JSONField

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

class CustomResource(ModelResource):
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
    
        return super(CustomResource, cls).api_field_from_django_field(f, default)

class SlugResource(CustomResource):
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

class CustomApiKeyAuthentication(ApiKeyAuthentication):
    """
    Custom API Auth that accepts parameters as cookies or headers as well as GET params.
    """
    def is_authenticated(self, request, **kwargs):
        email = request.COOKIES.get('email') or request.META.get('HTTP_PANDA_EMAIL') or request.GET.get('email')
        api_key = request.COOKIES.get('api_key') or request.META.get('HTTP_PANDA_API_KEY') or request.GET.get('api_key')

        if email:
            email = unquote(email)

        if not email or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(username=email.lower())
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user

        return self.get_key(user, api_key)

class CustomSerializer(Serializer):
    """
    A custom serializer that truncates microseconds from iso8601.
    """
    def format_datetime(self, data):
        return data.strftime('%Y-%m-%dT%H:%M:%S')

class CustomPaginator(Paginator):
    """
    A customized paginator that accepts count as a property, rather
    then inferring it from the length of the object array.
    """
    def __init__(self, request_data, objects, resource_uri=None, limit=None, offset=0, count=None):
        self.count = count
        super(CustomPaginator, self).__init__(request_data, objects, resource_uri, limit, offset)

    def get_count(self):
        if self.count is not None:
            return self.count
        
        return super(CustomPaginator, self).get_count()

