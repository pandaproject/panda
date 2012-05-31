#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaApiKeyAuthentication, PandaSerializer, PandaModelResource
from panda.models import SearchSubscription 

class SearchSubscriptionResource(PandaModelResource):
    """
    Access to user subscriptions.
    """
    from panda.api.datasets import DatasetResource

    dataset = fields.ForeignKey(DatasetResource, 'dataset', null=True)

    class Meta:
        queryset = SearchSubscription.objects.all()
        resource_name = 'search_subscription'
        
        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(SearchSubscriptionResource, self).obj_create(bundle, request, recipient=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(recipient=request.user)

    def save_related(self, bundle):
        """
        Overriding this is a bit of a dirty-hack, but we really don't want
        Dataset being saved whenever a subscription is updated (because it
        kicks off Solr indexing).
        """
        pass

