#!/bin/bash

# Set working directory
cd /opt/app

# Collect static files
echo "Collect static files"
python manage.py collectstatic --no-input

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --no-input

# Start server
echo "Starting server"
uwsgi --ini /opt/app/deploy/app_uwsgi.ini
