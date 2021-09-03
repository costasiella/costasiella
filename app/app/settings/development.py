"""
Django settings for development
"""
import sys
from app.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# This tests whether the second commandline argument (after ./manage.py) was test.
TESTING = False
if len(sys.argv) >= 1:
    if sys.argv[1] == 'test':
        TESTING = True

# Media files (User uploads)
# https://docs.djangoproject.com/en/2.1/topics/files/
if 'GITHUB_WORKFLOW' in os.environ:
    MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media_test")

## Email settings for development
# Console
# Uncomment below to print emails to the terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMTP
# Uncomment below to send emails using smtp
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_USE_TLS = False
# EMAIL_PORT = 2525
# EMAIL_HOST_USER = None
# EMAIL_HOST_PASSWORD = None

# Django-defender & celery use
DEFENDER_REDIS_URL = 'redis://localhost:6379/0'
CELERY_BROKER_URL = "redis://localhost:6379/1"
