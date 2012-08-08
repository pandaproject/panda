#!/usr/bin/env python

from tastypie import fields
from tastypie.authorization import DjangoAuthorization

from panda.api.utils import PandaAuthentication, PandaSerializer, PandaModelResource
from panda.models import SearchSubscription, UserProxy 

class SearchSubscriptionResource(PandaModelResource):
    """
    Access to user subscriptions.
    """
    from panda.api.category import CategoryResource
    from panda.api.datasets import DatasetResource

    dataset = fields.ForeignKey(DatasetResource, 'dataset', null=True, full=True)
    category = fields.ForeignKey(CategoryResource, 'category', null=True, full=True)

    class Meta:
        queryset = SearchSubscription.objects.all()
        resource_name = 'search_subscription'
        allowed_methods = ['get', 'post', 'delete']
        
        authentication = PandaAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        return super(SearchSubscriptionResource, self).obj_create(bundle, request, user=user)

    def apply_authorization_limits(self, request, object_list):
        # Because users may have authenticated via headers the request.user may
        # not be a full User instance. To be sure, we fetch one.
        user = UserProxy.objects.get(id=request.user.id)

        return object_list.filter(user=user)

    def save_related(self, bundle):
        """
        Overriding this is a bit of a dirty-hack, but we really don't want
        Dataset being saved whenever a subscription is updated (because it
        kicks off Solr indexing).
        """
        pass

