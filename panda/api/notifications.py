#!/usr/bin/env python

from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaAuthentication, PandaSerializer, PandaModelResource
from panda.models import Notification, UserProxy 

class NotificationResource(PandaModelResource):
    """
    Access to user notifications.
    """
    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        
        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

        filtering = {
            "read_at": ('isnull')
        }

    def obj_create(self, bundle, request=None, **kwargs):
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        return super(NotificationResource, self).obj_create(bundle, request, recipient=user)

    def apply_authorization_limits(self, request, object_list):
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        return object_list.filter(recipient=user)

    def save_related(self, bundle):
        """
        Overriding this is a bit of a dirty-hack, but we really don't want
        Dataset being saved whenever a notification is updated (because it
        kicks off Solr indexing).
        """
        pass

    def put_list(self, request, **kwargs):
        """
        Allow emulating a ``PATCH`` request by passing ``?patch=true``.
        (As a workaround for IE's broken XMLHttpRequest.)
        """
        if request.GET.get('patch', 'false').lower() == 'true':
            return super(NotificationResource, self).patch_list(request, **kwargs)
        else:
            return super(NotificationResource, self).put_list(request, **kwargs)

