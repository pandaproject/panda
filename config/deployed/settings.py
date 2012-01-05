#!/usr/bin/env python

from config.settings import *

import logging
log = logging.getLogger('settings')

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
    log.warn('EMAIL_HOST not configured!') 

