#!/usr/bin/env python

from config.settings import *

# Running in deployed mode
SETTINGS = 'deployed'

# Debug
DEBUG = False 
TEMPLATE_DEBUG = DEBUG

# Static media
STATIC_ROOT = '/var/lib/panda/media'

# Uploads 
MEDIA_ROOT = '/var/lib/panda/uploads' 
EXPORT_ROOT = '/var/lib/panda/exports'

# Solr
SOLR_DIRECTORY = '/opt/solr/panda/solr'

# Django-compressor
COMPRESS_ENABLED = True 

