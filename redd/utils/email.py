#!/usr/bin/env python

from django.conf import settings
from django.core.mail import send_mail

def panda_email(subject, message, recipients):
    send_mail('[PANDA] %s' % subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
