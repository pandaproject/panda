from config.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Database
DATABASES['default']['HOST'] = 'db'
DATABASES['default']['PORT'] = '5433'
DATABASES['default']['USER'] = 'panda'
DATABASES['default']['PASSWORD'] = 'NE3HY2dc16'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://media.panda.beta.tribapps.com/panda/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://media.panda.beta.tribapps.com/panda/admin_media/'

# Predefined domain
MY_SITE_DOMAIN = 'panda.panda.beta.tribapps.com'

# Email
EMAIL_HOST = 'mail'
EMAIL_PORT = 25

# Caching
CACHE_BACKEND = 'memcached://cache:11211/'

# S3
AWS_S3_URL = 's3://media.panda.beta.tribapps.com/panda/'

# Internal IPs for security
INTERNAL_IPS = ()

# logging
import logging.config
LOG_FILENAME = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logger.conf')
logging.config.fileConfig(LOG_FILENAME)
