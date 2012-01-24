#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization

from redd.api.utils import PandaApiKeyAuthentication, SluggedModelResource, PandaSerializer
from redd.models import Category

class CategoryResource(SluggedModelResource):
    """
    Simple wrapper around django-celery's task API.
    """
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        allowed_methods = ['get']

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

