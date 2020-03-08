"""
Django settings for development
"""

from app.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Media files (User uploads)
# https://docs.djangoproject.com/en/2.1/topics/files/
if 'TRAVIS' in os.environ:
    MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media_test")
