"""
Django settings for production deployment
"""
from os import path
from django.core.files.storage import FileSystemStorage
from app.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
CSRF_COOKIE_SECURE = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'My Name <my_from_email@domain.com>'

## Server error notifications
# All mail addresses listed in the ADMINS setting will receive server error notifications when DEBUG=False
##
# ADMINS = [
#     ('Full name', 'user@example.com'),
#     ('John', 'john@example.com')
# ]

## By default server error notifications are sent from root@localhost.
# Your email provider might reject emails from this address.
# The SERVER_EMAIL setting sets the address from which server errors are sent.
##
# SERVER_EMAIL = 'user@yourdomain.com'

# GraphQL JWT settings
GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=5),  # Default = 5 minutes
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),  # Default = 7 days
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_COOKIE_SECURE': True,
    'JWT_COOKIE_SAMESITE': 'Lax'
}

# Static files config
STATIC_ROOT = "/opt/static"
MEDIA_ROOT = "/opt/media"
MEDIA_PROTECTED_ROOT = "/opt/media_protected"
MEDIA_PROTECTED_STORAGE = FileSystemStorage(location=MEDIA_PROTECTED_ROOT, base_url=MEDIA_PROTECTED_PUBLIC_URL)

# Uncomment the line below to disable user signups
# ACCOUNT_ADAPTER = 'costasiella.allauth_adapters.account_adapter_no_signup.AccountAdapterNoSignup'

# Orphaned files cleanup
ORPHANED_APPS_MEDIABASE_DIRS = {
    'costasiella': {
        'root': MEDIA_ROOT,  # MEDIA_ROOT => default location(s) of your uploaded items e.g. /var/www/mediabase
        'skip': (               # optional iterable of subfolders to preserve, e.g. sorl.thumbnail cache
            path.join(MEDIA_ROOT, 'cache'),
        ),
        'exclude': ('.gitignore',)  # optional iterable of files to preserve
    }
}

# Point to redis container instead of localhost for Django-defender & celery
DEFENDER_REDIS_URL = 'redis://redis:6379/0'
CELERY_BROKER_URL = "redis://redis:6379/1"
