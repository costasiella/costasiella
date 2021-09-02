"""
Django settings for production deployment
"""
from app.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Static files config
STATIC_ROOT = "/opt/static"

# Point to redis container instead of localhost for Django-defender
DEFENDER_REDIS_URL = 'redis://redis:6379/0'

# Point to rabbitMQ container insteaf of localhost for celery
BROKER_URL = "amqp://guest:**@rabbitmq:5672//"
