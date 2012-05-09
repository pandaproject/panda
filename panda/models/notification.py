#!/user/bin/env python

from django.contrib.auth.models import User
from django.db import models

from panda.models.dataset import Dataset
from panda.models.export import Export
from panda.models.task_status import TaskStatus

NOTIFICATION_TYPE_CHOICES = (
    ('Info', 'Info'),
    ('Warning', 'Warning'),
    ('Error', 'Error')
)

class Notification(models.Model):
    """
    A user notification related to a task.
    """
    recipient = models.ForeignKey(User, related_name='notifications',
        help_text='The user who should receive this notification.')
    message = models.TextField(
        help_text='The message to deliver.')
    type = models.CharField(max_length=16, choices=NOTIFICATION_TYPE_CHOICES, default='Info',
        help_text='The type of message: info, warning or error')
    sent_at = models.DateTimeField(auto_now=True,
        help_text='When this notification was created')
    read_at = models.DateTimeField(null=True, blank=True, default=None,
        help_text='When this notification was read by the user.')
    related_task = models.ForeignKey(TaskStatus, null=True, default=None,
        help_text='A task related to this notification, if any.')
    related_dataset = models.ForeignKey(Dataset, null=True, default=None,
        help_text='A dataset related to this notification, if any.')
    related_export = models.ForeignKey(Export, null=True, default=None,
        help_text='A file export related to this notification, ifany.')

    class Meta:
        app_label = 'panda'
        ordering = ['-sent_at'] 

