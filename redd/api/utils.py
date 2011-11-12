#!/usr/bin/env python

from urllib import unquote

from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication
from tastypie.fields import ApiField, CharField
from tastypie.resources import ModelResource

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

class CustomApiKeyAuthentication(ApiKeyAuthentication):
    """
    Custom API Auth that accepts parameters as cookies or headers as well as GET params.
    """
    def is_authenticated(self, request, **kwargs):
        email = request.COOKIES.get('email') or request.META.get('HTTP_PANDA_EMAIL') or request.GET.get('email')
        api_key = request.COOKIES.get('api_key') or request.META.get('HTTP_PANDA_API_KEY') or request.GET.get('api_key')

        email = unquote(email)

        if not email or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(username=email.lower())
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user

        return self.get_key(user, api_key)

