#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaApiKeyAuthentication, PandaModelResource, PandaSerializer
from panda.models import ActivityLog 

class ActivityLogResource(PandaModelResource):
    """
    API resource for DataUploads.
    """
    from panda.api.users import UserResource

    creator = fields.ForeignKey(UserResource, 'user', full=True)

    class Meta:
        queryset = ActivityLog.objects.all()
        resource_name = 'activity_log'
        allowed_methods = ['get', 'post']

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Create an activity log for the accessing user.
        """
        bundle = super(ActivityLogResource, self).obj_create(bundle, request=request, user=request.user, **kwargs)

        return bundle

