#!/usr/bin/env python

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

class ActivityLog(models.Model):
    """
    A daily log of activity by a users.
    """
    user = models.ForeignKey(User, related_name='activity_logs',
        help_text='The user who was active.')
    when = models.DateField(
        help_text='The date this activity was recorded.')

    class Meta:
        app_label = 'panda'
        verbose_name_plural = 'ActivityLogs'
        unique_together = ('user', 'when')

    def __unicode__(self):
        return '%s at %s' % (self.user, self.when)

    def save(self, *args, **kwargs):
        if not self.when:
            self.when = now().date()

        super(ActivityLog, self).save(*args, **kwargs)

