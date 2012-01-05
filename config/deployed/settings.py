#!/usr/bin/env python

import logging
log = logging.getLogger('settings')

from config.settings import *

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
