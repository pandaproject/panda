#!/usr/bin/env python

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

ACTIVITY_CHOICES = [
    ('ON_SITE', 'ON_SITE'),
]

class ActivityLog(models.Model):
    """
    A log of some activity taken by a user.
    """
    user = models.ForeignKey(User,
        help_text='The user who was active.')
    activity = models.CharField(max_length=64, default='ON_SITE', choices=ACTIVITY_CHOICES,
        help_text='The activity being recorded'),
    when = models.DateTimeField(
        help_text='The date and time this activity was recorded.')

    class Meta:
        app_label = 'panda'
        verbose_name_plural = 'ActivityLogs'

    def __unicode__(self):
        return '%s at %s' % (self.user, self.when)

    def save(self, *args, **kwargs):
        if not self.when:
            self.when = now()

        super(ActivityLog, self).save(*args, **kwargs)

