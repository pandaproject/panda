#!/user/bin/env python

from django.db import models

from panda.models.user_proxy import UserProxy

NOTIFICATION_TYPE_CHOICES = (
    ('Info', 'Info'),
    ('Warning', 'Warning'),
    ('Error', 'Error')
)

class Notification(models.Model):
    """
    A user notification related to a task.
    """
    recipient = models.ForeignKey(UserProxy, related_name='notifications',
        help_text='The user who should receive this notification.')
    message = models.TextField(
        help_text='The message to deliver.')
    type = models.CharField(max_length=16, choices=NOTIFICATION_TYPE_CHOICES, default='Info',
        help_text='The type of message: info, warning or error')
    sent_at = models.DateTimeField(auto_now=True,
        help_text='When this notification was created')
    read_at = models.DateTimeField(null=True, blank=True, default=None,
        help_text='When this notification was read by the user.')
    url = models.URLField(null=True, default=None,
        help_text='A url to link to when displaying this notification.') 

    class Meta:
        app_label = 'panda'
        ordering = ['-sent_at'] 

