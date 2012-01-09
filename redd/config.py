#!/usr/bin/env python

from livesettings import config_register, BooleanValue, ConfigurationGroup, PositiveIntegerValue, StringValue

# Site domain settings
DOMAIN_GROUP = ConfigurationGroup(
    'DOMAIN',
    'Site domain settings',
    ordering=0
)

config_register(StringValue(
    DOMAIN_GROUP,
    'SITE_DOMAIN',
    description='Site domain to be referenced in outgoing email.',
    default='localhost:8000'
))

# Email settings
EMAIL_GROUP = ConfigurationGroup(
    'EMAIL',
    'Email settings',
    ordering=1
)

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST',
    description='Hostname or IP of the SMTP server to use for email.',
    default='localhost',
    ordering=0
))

config_register(PositiveIntegerValue(
    EMAIL_GROUP,
    'EMAIL_PORT',
    description='Hostname or IP of the SMTP server to use for email.',
    default=1025,
    ordering=1
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_USER',
    description='Username for the SMTP server to use for email. (Leave blank if authentication is not required.)',
    default='',
    ordering=2
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_PASSWORD',
    description='Password for the SMTP server to use for email. (Leave blank if authentication is not required.)',
    default='',
    ordering=3
))

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_USE_TLS',
    description='Whether or not to use TLS encryption when communicating with the SMTP server to use for email.',
    default=False,
    ordering=4
))

config_register(StringValue(
    EMAIL_GROUP,
    'DEFAULT_FROM_EMAIL',
    description='Email address that PANDA messages should appear to come from.',
    default='do.not.reply@pandaproject.net',
    ordering=5
))

