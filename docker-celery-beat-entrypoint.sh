#!/bin/bash

# Set working directory
cd /opt/app

# Collect static files
echo "Start celery beat"
celery -A app beat -l info
