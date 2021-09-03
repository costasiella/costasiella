#!/bin/bash

# Set working directory
cd /opt/app

# Collect static files
echo "Start celery"
celery -A app worker -l info
