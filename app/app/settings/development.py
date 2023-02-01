"""
Django settings for development
"""
import sys
from os import path
from app.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# This tests whether the second commandline argument (after ./manage.py) was test.
TESTING = False
if len(sys.argv) >= 1:
    if sys.argv[1] == 'test':
        TESTING = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'My Name <my_from_email@domain.com>'

# Media root
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media")
if 'GITHUB_WORKFLOW' in os.environ:
    MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media_test")

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

# Uncomment the line below to disable user signups
# ACCOUNT_ADAPTER = 'costasiella.allauth_adapters.account_adapter_no_signup.AccountAdapterNoSignup'

# Re-enable this once it doesn't break promises
# 'graphene_django.debug.DjangoDebugMiddleware'
if DEBUG:
    GRAPHENE['MIDDLEWARE'].append('costasiella.middlewares.DjangoDebugMiddleware')

# GraphQL JWT settings with long expiration. Uncomment during development if useful for graphiQL auth for example.
GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=5),  # Default = 5 minutes
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(minutes=30),  # Default = 7 days
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_COOKIE_SAMESITE': 'Lax'
}

# Django-defender & celery use
DEFENDER_REDIS_URL = 'redis://localhost:6379/0'
CELERY_BROKER_URL = "redis://localhost:6379/1"
