#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpConflict
from django.utils.translation import ugettext_lazy as _

from panda.api.utils import PandaAuthentication, PandaModelResource, PandaSerializer
from django.db import IntegrityError
from panda.models import ActivityLog, UserProxy

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

        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Create an activity log for the accessing user.
        """
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        try:
            bundle = super(ActivityLogResource, self).obj_create(bundle, request=request, user=user, **kwargs)
        except IntegrityError:
            raise ImmediateHttpResponse(response=HttpConflict(_('Activity has already been recorded.')))

        return bundle

