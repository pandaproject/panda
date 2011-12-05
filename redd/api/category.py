#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization

from redd.api.utils import CustomApiKeyAuthentication, SlugResource, CustomSerializer
from redd.models import Category

class CategoryResource(SlugResource):
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

