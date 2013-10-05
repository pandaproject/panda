#!/usr/bin/env python

from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.user_proxy import UserProxy

class ActivityLog(models.Model):
    """
    A daily log of activity by a users.
    """
    user = models.ForeignKey(UserProxy, related_name='activity_logs',
        help_text=_('The user who was active.'),
        verbose_name=_('user'))
    when = models.DateField(_('when'), auto_now=True,
        help_text=_('The date this activity was recorded.'))

    class Meta:
        app_label = 'panda'
        verbose_name = _('ActivityLog')
        verbose_name_plural = _('ActivityLogs')
        unique_together = ('user', 'when')

    def __unicode__(self):
        return _('%s at %s') % (self.user, self.when)

