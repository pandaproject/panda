#!/usr/bin/env python

from django.template.loader import get_template
from django.template import Context, TemplateDoesNotExist
from livesettings import config_value

from panda.utils.mail import send_mail

def get_message_template(prefix):
    return get_template('/'.join(['notifications', prefix, 'message.html']))

def get_email_subject_template(prefix):
    return get_template('/'.join(['notifications', prefix, 'email_subject.txt']))

def get_email_body_template(prefix):
    return get_template('/'.join(['notifications', prefix, 'email_body.txt']))

def notify(recipient, template_prefix, note_type, url=None, extra_context={}):
    """
    Notify a user of an event using the Notification system and
    email.
    """
    from panda.models import Notification

    context = Context({
        'recipient': recipient,
        'type': note_type,
        'url': url,
        'site_domain': config_value('DOMAIN', 'SITE_DOMAIN')
    })
    context.update(extra_context)

    message = get_message_template(template_prefix).render(context) 
    
    Notification.objects.create(
        recipient=recipient,
        message=message,
        type=note_type,
        url=url
    )

    # Don't HTML escape plain-text emails
    context.autoescape = False

    try:
        email_subject = get_email_subject_template(template_prefix).render(context)
    except TemplateDoesNotExist:
        email_subject = message

    try:
        email_message = get_email_body_template(template_prefix).render(context)
    except TemplateDoesNotExist:
        email_message = message
    
    send_mail(email_subject.strip(), email_message, [recipient.username])

