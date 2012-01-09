#!/usr/bin/env python

from config.settings import *

# Running in deployed mode
SETTINGS = 'deployed'

# Debug
DEBUG = True    # TEMP 
TEMPLATE_DEBUG = DEBUG

# Static media
STATIC_ROOT = '/mnt/media'

# Uploads 
MEDIA_ROOT = '/mnt/panda' 

# Django-compressor
COMPRESS_ENABLED = True 

