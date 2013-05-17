#!/user/bin/env python

from django.db import models
from django.utils.translation import ugettext_lazy as _

from panda.models.user_proxy import UserProxy

NOTIFICATION_TYPE_CHOICES = (
    ('Info', _('Info')),
    ('Warning', _('Warning')),
    ('Error', _('Error'))
)

class Notification(models.Model):
    """
    A user notification related to a task.
    """
    recipient = models.ForeignKey(UserProxy, related_name='notifications',
        help_text=_('The user who should receive this notification.'),
        verbose_name=_('recipient'))
    message = models.TextField(_('message'),
        help_text=_('The message to deliver.'))
    type = models.CharField(_('type'), max_length=16, choices=NOTIFICATION_TYPE_CHOICES, default='Info',
        help_text=_('The type of message: info, warning or error'))
    sent_at = models.DateTimeField(_('sent_at'), auto_now=True,
        help_text=_('When this notification was created'))
    read_at = models.DateTimeField(_('read_at'), null=True, blank=True, default=None,
        help_text=_('When this notification was read by the user.'))
    url = models.URLField(_('url'), null=True, default=None,
        help_text=_('A url to link to when displaying this notification.')) 

    class Meta:
        app_label = 'panda'
        ordering = ['-sent_at'] 
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
