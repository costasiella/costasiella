"""
Django settings for development
"""

from app.settings.common import *

# Media files (User uploads)
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_ROOT = os.path.join(os.getcwd(), "costasiella", "media_test")
