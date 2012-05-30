#!/usr/bin/env python

from panda.utils.mail import send_mail

def notify(recipient, message, note_type, related_task=None, related_dataset=None, related_export=None, email_subject=None, email_message=None):
    """
    Notify a user of an event using the Notification system and
    email.
    """
    from panda.models import Notification
    
    Notification.objects.create(
        recipient=recipient,
        related_task=related_task,
        related_dataset=related_dataset,
        related_export=related_export,
        message=message,
        type=note_type
    )

    if not email_subject:
        email_subject = message

    if not email_message:
        email_message = message
    
    send_mail(email_subject, email_message, [recipient.username])

