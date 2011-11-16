#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from redd.api.utils import CustomApiKeyAuthentication, CustomSerializer
from redd.models import Category

class CategoryResource(ModelResource):
    """
    Simple wrapper around django-celery's task API.
    """
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()

