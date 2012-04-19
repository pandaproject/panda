#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpConflict

from panda.api.utils import PandaApiKeyAuthentication, PandaModelResource, PandaSerializer
from django.db import IntegrityError
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
        try:
            bundle = super(ActivityLogResource, self).obj_create(bundle, request=request, user=request.user, **kwargs)
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpConflict('Activity has already been recorded.'))

        return bundle

