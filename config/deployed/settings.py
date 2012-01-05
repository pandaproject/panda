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
    print 'WARNING: Running in production mode, but EMAIL_HOST is set to localhost!'

