#!/usr/bin/env python

from django.core import mail
from livesettings import config_value

def get_connection():
    return mail.get_connection(
        host=config_value('EMAIL', 'EMAIL_HOST'),
        port=config_value('EMAIL', 'EMAIL_PORT'),
        # See http://bugs.python.org/issue8489
        username=str(config_value('EMAIL', 'EMAIL_HOST_USER')),
        password=str(config_value('EMAIL', 'EMAIL_HOST_PASSWORD')),
        use_tls=config_value('EMAIL', 'EMAIL_USE_TLS')) 

def send_mail(subject, message, recipients):
    mail.send_mail('[PANDA] %s' % subject, message, str(config_value('EMAIL', 'DEFAULT_FROM_EMAIL')), recipients, connection=get_connection())

