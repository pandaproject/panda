#!/usr/bin/env python

from livesettings import config_register, BooleanValue, ConfigurationGroup, FloatValue, PositiveIntegerValue, StringValue

# Site domain settings
DOMAIN_GROUP = ConfigurationGroup(
    'DOMAIN',
    'Site domain',
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
    'Email',
    ordering=1
)

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_ENABLED',
    description='Enable email?',
    help_text='If enabled, notifications and activation messages will be sent via email.',
    default=False,
    ordering=0
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST',
    description='Hostname or IP of the SMTP server.',
    default='localhost',
    ordering=1
))

config_register(PositiveIntegerValue(
    EMAIL_GROUP,
    'EMAIL_PORT',
    description='Port number of the SMTP server.',
    default=1025,
    ordering=2
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_USER',
    description='Username for the SMTP server.',
    default='',
    ordering=3
))

config_register(StringValue(
    EMAIL_GROUP,
    'EMAIL_HOST_PASSWORD',
    description='Password for the SMTP server.',
    default='',
    ordering=4
))

config_register(BooleanValue(
    EMAIL_GROUP,
    'EMAIL_USE_TLS',
    description='Use TLS encryption when connecting to the SMTP server?',
    default=False,
    ordering=5
))

config_register(StringValue(
    EMAIL_GROUP,
    'DEFAULT_FROM_EMAIL',
    description='Email address that PANDA messages should appear to come from.',
    default='do.not.reply@pandaproject.net',
    ordering=6
))

# Miscellaneous settings
MISC_GROUP = ConfigurationGroup(
    'MISC',
    'Miscellaneous',
    ordering=2
)

config_register(PositiveIntegerValue(
    MISC_GROUP,
    'MAX_UPLOAD_SIZE',
    description='Maximum size allowed for user-uploaded files, in bytes.',
    help_text='The default value is equivalent to 1GB.',
    default=1073741824,
    ordering=0
))

config_register(BooleanValue(
    MISC_GROUP,
    'DEMO_MODE',
    description='Enable demo mode?',
    help_text='Displays default credentials on login screen.',
    default=False,
    ordering=1
))

# Performance settings
PERF_GROUP = ConfigurationGroup(
    'PERF',
    'Performance',
    ordering=3
)

config_register(FloatValue(
    PERF_GROUP,
    'TASK_THROTTLE',
    description='Number of seconds to wait between processing batches of data.',
    help_text='A larger number will result in slower imports and exports, but better responsiveness from the PANDA user interface.',
    default=0.5,
    ordering=1
))

