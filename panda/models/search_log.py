#!/usr/bin/env python

from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.dataset import Dataset
from panda.models.user_proxy import UserProxy

class SearchLog(models.Model):
    """
    A log of a user search.
    """
    user = models.ForeignKey(UserProxy, related_name='search_logs',
        help_text=_('The user who executed the search.'),
        verbose_name=_('user'))
    dataset = models.ForeignKey(Dataset, related_name='searches', null=True, default=None,
        help_text=_('The data set searched, or null if all were searched.'),
        verbose_name=_('dataset'))
    query = models.CharField(_('query'), max_length=4096, 
        help_text=_('The search query that was executed'))
    when = models.DateTimeField(_('when'), auto_now=True,
        help_text=_('The date and time this search was logged.'))

    class Meta:
        app_label = 'panda'
        verbose_name = _('SearchLog')
        verbose_name_plural = _('SearchLogs')

    def __unicode__(self):
        if self.dataset:
            return _('%(user)s searched %(dataset)s for %(query)s') \
                % {'user': self.user, 'dataset': self.dataset, 'query': self.query}
        else:
            return _('%(user)s searched for %(query)s') \
                % {'user': self.user, 'query': self.query}

