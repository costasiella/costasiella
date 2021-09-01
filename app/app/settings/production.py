"""
Django settings for production deployment
"""
from app.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Static files config
STATIC_ROOT = "/opt/static"
