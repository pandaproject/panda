#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from redd.api.utils import CustomApiKeyAuthentication
from redd.models import Notification 

class NotificationResource(ModelResource):
    """
    Access to user notifications.
    """
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        allowed_methods = ['get']
        
        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(NotificationResource, self).obj_create(bundle, request, recipient=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(recipient=request.user)

