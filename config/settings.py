#!/usr/bin/env python

import os

import django

# Base paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Debugging
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Default connection to socket
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'panda',
        'USER': 'panda',
        'PASSWORD': 'panda'
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

# Media
STATIC_ROOT = os.path.join(SITE_ROOT, 'media')
STATIC_URL = '/site_media/'
ADMIN_MEDIA_PREFIX = '/site_media/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Uploads
MEDIA_ROOT = '/tmp/panda'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-lyd+@8@=9oni01+gjvb(txz3%hh_7a9m5*n0q^ce5+&c1fkm('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.staticfiles',

    'djcelery',
    'compressor',

    'redd',
    'forest'
)

# Email
# run "python -m smtpd -n -c DebuggingServer localhost:1025" to see outgoing
# messages dumped to the terminal
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'do.not.reply@panda.tribapps.com'

# Django-compressor
COMPRESS_ENABLED = False 

# Celery
import djcelery
djcelery.setup_loader()

BROKER_TRANSPORT = "sqlakombu.transport.Transport"
BROKER_HOST = "postgresql:///panda?user=panda&password=panda"
CELERY_RESULT_DBURI = "postgresql:///panda?user=panda&password=panda"
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_CONCURRENCY = 1
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {  
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'default': {
            'level':'INFO',
            'class':'loghandlers.GroupWriteRotatingFileHandler',
            'filename': '/var/log/panda/panda.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'request_handler': {
                'level':'INFO',
                'class':'loghandlers.GroupWriteRotatingFileHandler',
                'filename': '/var/log/panda/requests.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'standard',
        },  
        'backend_handler': {
                'level':'DEBUG',
                'class':'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db': { 
            'handlers': ['backend_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# Solr
SOLR_ENDPOINT = 'http://localhost:8983/solr/data'

# Miscellaneous configuration
PANDA_DEFAULT_SEARCH_ROWS = 10
PANDA_DEFAULT_SEARCH_GROUPS = 10

# Allow for local (per-user) override
try:
    from local_settings import *
except ImportError:
    pass

