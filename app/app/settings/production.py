"""
Django settings for production deployment
"""
from os import path
from app.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'My Name <my_from_email@domain.com>'

# Static files config
STATIC_ROOT = "/opt/static"
MEDIA_ROOT = "/opt/media"

# Orphaned files cleanup
ORPHANED_APPS_MEDIABASE_DIRS = {
    'costasiella': {
        'root': MEDIA_ROOT,  # MEDIA_ROOT => default location(s) of your uploaded items e.g. /var/www/mediabase
        'skip': (               # optional iterable of subfolders to preserve, e.g. sorl.thumbnail cache
            path.join(MEDIA_ROOT, 'cache'),
        ),
        'exclude': ('.gitignore',) # optional iterable of files to preserve
    }
}

# Point to redis container instead of localhost for Django-defender & celery
DEFENDER_REDIS_URL = 'redis://redis:6379/0'
CELERY_BROKER_URL = "redis://redis:6379/1"
