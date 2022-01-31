#!/bin/bash

# Set working directory
cd /opt/app

# Start celery
echo "Start celery"
celery -A app worker -l info
