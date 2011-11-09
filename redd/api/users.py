#!/usr/bin/env python

from django.contrib.auth.models import User
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from redd.api.utils import CustomApiKeyAuthentication

class UserResource(ModelResource):
    """
    API resource for Uploads.
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get']
        excludes = ['password']

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()

