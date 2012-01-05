#!/usr/bin/env python

from config.settings import *

SETTINGS = 'deployed'

DEBUG = True 
TEMPLATE_DEBUG = DEBUG

# Static media
STATIC_ROOT = '/mnt/media'

# Uploads 
MEDIA_ROOT = '/mnt/panda' 

# Django-compressor
COMPRESS_ENABLED = True 

if EMAIL_HOST == 'localhost':
    raise ValueError('EMAIL_HOST not configured!')

