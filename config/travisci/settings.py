#!/usr/bin/env python

from config.settings import *

# Running in deployed mode
SETTINGS = 'travisci'

# Debug
DEBUG = True 
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'PORT': '5432',
        'NAME': 'panda',
        'USER': 'postgres'
    }
}

TEST_RUNNER = 'config.travisci.test_runner.ExistingDatabaseTestRunner'

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
        'backend_handler': {
                'level':'DEBUG',
                'class':'django.utils.log.NullHandler',
        },
    },
   'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['console'],
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
