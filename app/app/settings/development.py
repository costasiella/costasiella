"""
Django settings for development
"""
import sys
from os import path
from app.settings.common import *

from django.core.files.storage import FileSystemStorage

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

##
# CSRF Settings
##
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://dev.costasiella.com:3000',
    'http://localhost:3001',
    'http://dev.costasiella.com:3001'
]


# Media root
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media")
if 'GITHUB_WORKFLOW' in os.environ:
    MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media_test")

# Protected media root
MEDIA_PROTECTED_ROOT = os.path.join(os.getcwd(), "costasiella", "media_protected")
if 'GITHUB_WORKFLOW' in os.environ:
    MEDIA_PROTECTED_ROOT = os.path.join(os.getcwd(), "costasiella", "media_protected_test")
MEDIA_PROTECTED_STORAGE = FileSystemStorage(location=MEDIA_PROTECTED_ROOT, base_url=MEDIA_PROTECTED_PUBLIC_URL)

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
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),  # Default = 7 days
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_COOKIE_SAMESITE': 'Lax'
}

# Django-defender & celery use
DEFENDER_REDIS_URL = 'redis://localhost:6379/0'
CELERY_BROKER_URL = "redis://localhost:6379/1"

"""
Sportbit Mapping for subscriptions
+----+-------------------+
| id | name              |
+----+-------------------+
|  1 | BASIC             |
|  2 | MEDIUM            |
|  3 | BASIC (6 maanden) |
|  4 | Docent            |
|  5 | Xustom 2x         |
|  6 | PREMIUM           |
|  7 | Xustom 1x         |
|  8 | Xustom 0x         |
+----+-------------------+
"""
SPORTBIT_MAP_SUBSCRIPTIONS = {
        1: 3, # Basic
        2: 4, # Medium
        6: 5, # Premium
        4: 6, # Docent
        7: 7, # Xustom 1x
        5: 8  # Xustom 2x
    }

"""
Sportbit mapping for clases
+----+-----------+-----------------+-----------------+---------+-----------------+
| id | day_name  | time_start      | time_end        | name    | name            |
+----+-----------+-----------------+-----------------+---------+-----------------+
|  7 | Monday    | 09:30:00.000000 | 10:45:00.000000 | YogaWrt | Yin Yoga        |
|  4 | Monday    | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Yin Yoga        |
|  2 | Monday    | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Power Yoga      |
| 36 | Monday    | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Yin Yoga        |
|  5 | Tuesday   | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Power Yoga      |
|  1 | Tuesday   | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Yin Yoga        |
| 28 | Tuesday   | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Yin Yoga        |
| 40 | Wednesday | 09:00:00.000000 | 10:15:00.000000 | YogaWrt | Power Yoga      |
|  3 | Wednesday | 10:30:00.000000 | 11:45:00.000000 | YogaWrt | Yin Yoga        |
| 11 | Wednesday | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Power Yoga      |
| 37 | Wednesday | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Yin Yoga        |
| 13 | Wednesday | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Yin Yoga        |
| 12 | Wednesday | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Power Yoga      |
| 38 | Thursday  | 19:00:00.000000 | 20:15:00.000000 | YogaWrt | Yin Yoga        |
| 44 | Thursday  | 20:30:00.000000 | 21:45:00.000000 | YogaWrt | Hatha Flow Yoga |
| 16 | Saturday  | 09:00:00.000000 | 10:15:00.000000 | YogaWrt | Power Yoga      |
| 17 | Saturday  | 10:30:00.000000 | 11:45:00.000000 | YogaWrt | Yin Yoga        |
+----+-----------+-----------------+-----------------+---------+-----------------+
"""
SPORTBIT_MAP_CLASSES = {
    7: 18,
    4: 8,
    2: 9,
    36: 11,
    5: 12,
    1: 10,
    28: 13,
    40: 2,
    3: 3,
    11: 16,
    37: 15,
    13: 14,
    12: 17,
    38: 7,
    44: 6,
    16: 4,
    17: 5
}
