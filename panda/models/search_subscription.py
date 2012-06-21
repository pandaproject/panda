#!/usr/bin/env python

from django.db import models

from panda.models.category import Category
from panda.models.dataset import Dataset
from panda.models.user_proxy import UserProxy

class SearchSubscription(models.Model):
    """
    A log of a user search.
    """
    user = models.ForeignKey(UserProxy, related_name='search_subscriptions',
        help_text='The user who subscribed to the search.')
    dataset = models.ForeignKey(Dataset, related_name='search_subscriptions', null=True, default=None,
        help_text='The dataset to be searched or null if all are to be searched.')
    category = models.ForeignKey(Category, related_name='search_subscriptions', null=True, default=None,
        help_text='A category to be searched or null if all are to be searched.')
    query = models.CharField(max_length=256, 
        help_text='The search query to executed.')
    query_url = models.CharField(max_length=256,
        help_text='Query encoded for URL.')
    query_human = models.TextField(
        help_text='Human-readable description of the query being run.')
    last_run = models.DateTimeField(auto_now=True,
        help_text='The last time this search this was run.')

    class Meta:
        app_label = 'panda'
        verbose_name_plural = 'SearchSubscription'

    def __unicode__(self):
        if self.dataset:
            return '%s is searching for %s in %s' % (self.user, self.query, self.dataset)
        else:
            return '%s is searching for %s in all datasets' % (self.user, self.query)

