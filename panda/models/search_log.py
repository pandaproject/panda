#!/usr/bin/env python

from django.db import models

from panda.models.dataset import Dataset
from panda.models.user_proxy import UserProxy

class SearchLog(models.Model):
    """
    A log of a user search.
    """
    user = models.ForeignKey(UserProxy, related_name='search_logs',
        help_text='The user who executed the search.')
    dataset = models.ForeignKey(Dataset, related_name='searches', null=True, default=None,
        help_text='The data set searched, or null if all were searched.')
    query = models.CharField(max_length=4096, 
        help_text='The search query that was executed')
    when = models.DateTimeField(auto_now=True,
        help_text='The date and time this search was logged.')

    class Meta:
        app_label = 'panda'
        verbose_name_plural = 'SearchLogs'

    def __unicode__(self):
        if self.dataset:
            return '%s searched %s for %s' % (self.user, self.dataset, self.query)
        else:
            return '%s searched for %s' % (self.user, self.query)

