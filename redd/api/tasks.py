#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from redd.api.utils import CustomApiKeyAuthentication, CustomSerializer
from redd.models import TaskStatus

class TaskResource(ModelResource):
    """
    Simple wrapper around django-celery's task API.
    """
    class Meta:
        queryset = TaskStatus.objects.all()
        resource_name = 'task'
        allowed_methods = ['get']
        
        filtering = {
            'status': ('exact', 'in', ),
            'end': ('year', 'month', 'day')
        }

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()

