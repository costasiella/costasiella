#!/bin/bash

# Set working directory
cd /opt/app

# Start celery beat
echo "Start celery beat"
celery -A app beat -S django -l info
