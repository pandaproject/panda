#!/usr/bin/env python

from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.category import Category
from panda.models.dataset import Dataset
from panda.models.user_proxy import UserProxy

class SearchSubscription(models.Model):
    """
    A log of a user search.
    """
    user = models.ForeignKey(UserProxy, related_name='search_subscriptions',
        help_text=_('The user who subscribed to the search.'),
        verbose_name=_('user'))
    dataset = models.ForeignKey(Dataset, related_name='search_subscriptions', null=True, default=None,
        help_text=_('The dataset to be searched or null if all are to be searched.'),
        verbose_name=_('dataset'))
    category = models.ForeignKey(Category, related_name='search_subscriptions', null=True, default=None,
        help_text=_('A category to be searched or null if all are to be searched.'),
        verbose_name=_('category'))
    query = models.CharField(_('query'), max_length=256, 
        help_text=_('The search query to executed.'))
    query_url = models.CharField(_('query_url'), max_length=256,
        help_text=_('Query encoded for URL.'))
    query_human = models.TextField(_('query_human'),
        help_text=_('Human-readable description of the query being run.'))
    last_run = models.DateTimeField(_('last_run'), auto_now=True,
        help_text=_('The last time this search this was run.'))

    class Meta:
        app_label = 'panda'
        verbose_name = _('SearchSubscription')
        verbose_name_plural = _('SearchSubscriptions')

    def __unicode__(self):
        if self.dataset:
            return _('%(user)s is searching for %(query)s in %(dataset)s') \
                % {'user': self.user, 'query': self.query, 'dataset': self.dataset}
        else:
            return _('%(user)s is searching for %(query)s in all datasets') \
                % {'user': self.user, 'query': self.query}


