import logging
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
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/site_media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

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
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
    'django.contrib.sitemaps',

    'djcelery',

    'redd'
)

# Predefined domain
MY_SITE_DOMAIN = 'localhost:8000'

# Email
# run "python -m smtpd -n -c DebuggingServer localhost:1025" to see outgoing
# messages dumped to the terminal
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'do.not.reply@panda.tribapps.com'

# Celery
import djcelery
djcelery.setup_loader()

BROKER_TRANSPORT = "sqlakombu.transport.Transport"
BROKER_HOST = "postgresql:///panda?user=panda&password=panda"
CELERY_RESULT_DBURI = "postgresql:///panda?user=panda&password=panda"

CELERY_QUEUES = {
    "default": {
        "exchange": "default",
        "binding_key": "default"},
    "import": {
        "exchange": "default",
        "binding_key": "import",
    }
}
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"

# Logging
logging.basicConfig(
    level=logging.DEBUG,
)

# Solr
SOLR_ENDPOINT = 'http://localhost:8983/solr'

# PANDA
PANDA_STORAGE_LOCATION = '/tmp/panda'

# Allow for local (per-user) override
try:
    from local_settings import *
except ImportError:
    pass
