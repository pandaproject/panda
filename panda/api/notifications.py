#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaApiKeyAuthentication, PandaSerializer, PandaModelResource
from panda.models import Notification 

class NotificationResource(PandaModelResource):
    """
    Access to user notifications.
    """
    from panda.api.datasets import DatasetResource
    from panda.api.tasks import TaskResource

    related_dataset = fields.ForeignKey(DatasetResource, 'related_dataset')
    related_task = fields.ToOneField(TaskResource, 'related_task')

    class Meta:
        queryset = Notification.objects.all()
        resource_name = 'notification'
        limit = 1000    # Don't paginate notifications
        
        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

        filtering = {
            "read_at": ('isnull')
        }

    def obj_create(self, bundle, request=None, **kwargs):
        return super(NotificationResource, self).obj_create(bundle, request, recipient=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(recipient=request.user)

    def save_related(self, bundle):
        """
        Overriding this is a bit of a dirty-hack, but we really don't want
        Dataset being saved whenever a notification is updated (because it
        kicks off Solr indexing).
        """
        pass

    #def alter_list_data_to_serialize(request, data):
        # TODO: trim paging data
        #return data

