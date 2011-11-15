#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from redd.api.utils import CustomApiKeyAuthentication, CustomSerializer
from redd.models import Notification 

class NotificationResource(ModelResource):
    """
    Access to user notifications.
    """
    from redd.api.datasets import DatasetResource
    from redd.api.tasks import TaskResource

    related_dataset = fields.ForeignKey(DatasetResource, 'related_dataset')
    related_task = fields.ToOneField(TaskResource, 'related_task')

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        allowed_methods = ['get']
        limit = 1000    # Don't paginate notifications
        
        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = CustomSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(NotificationResource, self).obj_create(bundle, request, recipient=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(recipient=request.user)

    #def alter_list_data_to_serialize(request, data):
        # TODO: trim paging data
        #return data

