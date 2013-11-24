#!/usr/bin/env python

from livesettings import config_register, BooleanValue, ConfigurationGroup, FloatValue, PositiveIntegerValue, StringValue
from django.utils.translation import ugettext_lazy as _

# Site domain settings
DOMAIN_GROUP = ConfigurationGroup(
    'DOMAIN',
    _('Site domain'),
    ordering=0
)

config_register(StringValue(
    DOMAIN_GROUP,
    'SITE_DOMAIN',
    description=_('Site domain to be referenced in outgoing email.'),
    default='localhost:8000'
))

# Email settings
EMAIL_GROUP = ConfigurationGroup(
    'EMAIL',
    _('Email'),
    ordering=1
)

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_ENABLED',
    description=_('Enable email?'),
    help_text=_('If enabled, notifications and activation messages will be sent via email.'),
    default=False,
    ordering=0
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST',
    description=_('Hostname or IP of the SMTP server.'),
    default='localhost',
    ordering=1
))

config_register(PositiveIntegerValue(
    EMAIL_GROUP,
    'EMAIL_PORT',
    description=_('Port number of the SMTP server.'),
    default=1025,
    ordering=2
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_USER',
    description=_('Username for the SMTP server.'),
    default='',
    ordering=3
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_PASSWORD',
    description=_('Password for the SMTP server.'),
    default='',
    ordering=4
))

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_USE_TLS',
    description=_('Use TLS encryption when connecting to the SMTP server?'),
    default=False,
    ordering=5
))

config_register(StringValue(
    EMAIL_GROUP,
    'DEFAULT_FROM_EMAIL',
    description=_('Email address that PANDA messages should appear to come from.'),
    default='do.not.reply@pandaproject.net',
    ordering=6
))

# Miscellaneous settings
MISC_GROUP = ConfigurationGroup(
    'MISC',
    _('Miscellaneous'),
    ordering=2
)

config_register(BooleanValue(
    MISC_GROUP,
    'DEMO_MODE_ENABLED',
    description=_('Enable demo mode?'),
    help_text=_('In demo mode the login fields will automatically be prepopulated with the default username and password.'),
    default=False,
    ordering=0
))

config_register(PositiveIntegerValue(
    MISC_GROUP,
    'WARN_UPLOAD_SIZE',
    description=_('File size at which a warning about large file uploads is issued, in bytes.'),
    help_text=_('The default value is equivalent to 100MB.'),
    default=104857600,
    ordering=1
))

config_register(PositiveIntegerValue(
    MISC_GROUP,
    'MAX_UPLOAD_SIZE',
    description=_('Maximum size allowed for user-uploaded files, in bytes.'),
    help_text=_('The default value is equivalent to 1GB.'),
    default=1073741824,
    ordering=2
))

# Performance settings
PERF_GROUP = ConfigurationGroup(
    'PERF',
    _('Performance'),
    ordering=3
)

config_register(FloatValue(
    PERF_GROUP,
    'TASK_THROTTLE',
    description=_('Number of seconds to wait between processing batches of data.'),
    help_text=_('A larger number will result in slower imports and exports, but better responsiveness from the PANDA user interface.'),
    default=0.5,
    ordering=1
))

