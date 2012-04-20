#!/usr/bin/env python

from django.contrib.auth.models import User
from django.db import models

class ActivityLog(models.Model):
    """
    A daily log of activity by a users.
    """
    user = models.ForeignKey(User, related_name='activity_logs',
        help_text='The user who was active.')
    when = models.DateField(auto_now=True,
        help_text='The date this activity was recorded.')

    class Meta:
        app_label = 'panda'
        verbose_name_plural = 'ActivityLogs'
        unique_together = ('user', 'when')

    def __unicode__(self):
        return '%s at %s' % (self.user, self.when)

