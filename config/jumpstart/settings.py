#!/usr/bin/env python

from config.settings import *
from config.deployed.settings import *

# Running in deployed mode
SETTINGS = 'jumpstart'

INSTALLED_APPS = (
    'longerusername',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'south',
    'tastypie',
    'djcelery',
    'compressor',
    'livesettings',

    'jumpstart'
)

try:
    from local_settings import *
except ImportError:
    pass

