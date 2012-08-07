#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaAuthentication, PandaSerializer, PandaModelResource
from panda.models import TaskStatus

class TaskResource(PandaModelResource):
    """
    Simple wrapper around django-celery's task API.
    """
    from panda.api.users import UserResource

    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        queryset = TaskStatus.objects.all()
        resource_name = 'task'
        allowed_methods = ['get']
        
        filtering = {
            'status': ('exact', 'in', ),
            'end': ('year', 'month', 'day')
        }

        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

