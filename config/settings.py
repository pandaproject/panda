#!/usr/bin/env python

import datetime
import os

import django

# Which settings are we using?
# Useful for debugging.
SETTINGS = 'base'

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

LOGIN_URL = '/admin/login/'
LOGOUT_URL = '/admin/logout/'
LOGIN_REDIRECT_URL = '/admin/'

SITE_ID = 1

# Default connection to socket
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'PORT': '5432',
        'NAME': 'panda',
        'USER': 'panda',
        'PASSWORD': 'panda'
    }
}

TIME_ZONE = 'Etc/UTC' 
USE_TZ = True 

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
EXPORT_ROOT = '/tmp/panda_exports'

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
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'config.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates')
)

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

    'jumpstart',
    'panda',
    'client'
)

SESSION_COOKIE_AGE = 2592000    # 30 days

AUTH_PROFILE_MODULE = 'panda.UserProfile'

# Django-compressor
COMPRESS_ENABLED = False 

# Celery
import djcelery
djcelery.setup_loader()

BROKER_TRANSPORT = 'sqlalchemy'
BROKER_URL = 'postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s/%(NAME)s' % DATABASES['default']
CELERY_RESULT_DBURI = 'postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s/%(NAME)s' % DATABASES['default'] 
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_CONCURRENCY = 1
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERYBEAT_SCHEDULE_FILENAME = 'celerybeat-schedule'

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'purge_orphaned_uploads': {
        'task': 'panda.tasks.cron.purge_orphaned_uploads',
        'schedule': crontab(minute=0, hour=2),
        'kwargs': { 'fake': False }
    },
    'run_subscriptions': {
        'task': 'panda.tasks.cron.run_subscriptions',
        'schedule': crontab(minute=30, hour=2)
    },
    'run_admin_alerts': {
        'task': 'panda.tasks.cron.run_admin_alerts',
        'schedule': crontab(minute=0, hour=4)
    }
}

# South
SOUTH_TESTS_MIGRATE = False

# Hack, see: http://stackoverflow.com/questions/3898239/souths-syncdb-migrate-creates-pages-of-output
import south.logger

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
        'south': {
            'handlers': ['console'],
            'level': 'INFO',
            'propogate': False
        },
        'keyedcache': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propogate': False
        },
        'requests.packages.urllib3.connectionpool': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propogate': False
        }
    }
}

# Solr
SOLR_ENDPOINT = 'http://localhost:8983/solr'
SOLR_DATA_CORE = 'data'
SOLR_DATASETS_CORE = 'datasets'
SOLR_DIRECTORY = '/var/solr'

# Miscellaneous configuration
PANDA_VERSION = '1.0.1'
PANDA_DEFAULT_SEARCH_GROUPS = 10
PANDA_DEFAULT_SEARCH_ROWS_PER_GROUP = 5
PANDA_DEFAULT_SEARCH_ROWS = 50
PANDA_SNIFFER_MAX_SAMPLE_SIZE = 1024 * 100  # 100kb
PANDA_SAMPLE_DATA_ROWS = 5
PANDA_SCHEMA_SAMPLE_ROWS = 100
PANDA_ACTIVATION_PERIOD = datetime.timedelta(days=30)
PANDA_AVAILABLE_SPACE_WARN = 1024 * 1024 * 1024 * 2 # 2GB
PANDA_AVAILABLE_SPACE_CRITICAL = 1024 * 1024 * 1024 * 1 # 1GB
PANDA_NOTIFICATIONS_TO_SHOW = 50

PANDA_UNCATEGORIZED_ID = 0
PANDA_UNCATEGORIZED_SLUG = 'uncategorized'
PANDA_UNCATEGORIZED_NAME = 'Uncategorized'

# Allow for local (per-user) override
try:
    from local_settings import *
except ImportError:
    pass

