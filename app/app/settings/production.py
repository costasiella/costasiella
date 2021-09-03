"""
Django settings for production deployment
"""
from app.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Static files config
STATIC_ROOT = "/opt/static"

# Point to redis container instead of localhost for Django-defender & celery
DEFENDER_REDIS_URL = 'redis://redis:6379/0'
CELERY_BROKER_URL = "redis://redis:6379/1"
