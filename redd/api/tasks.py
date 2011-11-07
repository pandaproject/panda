#!/usr/bin/env python

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from redd.models import TaskStatus

class TaskResource(ModelResource):
    """
    Simple wrapper around django-celery's task API.

    TKTK: implement authentication/permissions
    """
    class Meta:
        queryset = TaskStatus.objects.all()
        resource_name = 'task'
        allowed_methods = ['get']
        
        filtering = {
            'status': ('exact', 'in', ),
            'end': ('year', 'month', 'day')
        }

        authentication = Authentication()
        authorization = Authorization()
