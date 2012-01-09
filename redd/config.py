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
    description='Hostname or IP of the SMTP server.',
    default='localhost',
    ordering=0
))

config_register(PositiveIntegerValue(
    EMAIL_GROUP,
    'EMAIL_PORT',
    description='Port number of the SMTP server.',
    default=1025,
    ordering=1
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_USER',
    description='Username for the SMTP server.',
    default='',
    ordering=2
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_PASSWORD',
    description='Password for the SMTP server.',
    default='',
    ordering=3
))

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_USE_TLS',
    description='Use TLS encryption when connecting to the SMTP server?',
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

