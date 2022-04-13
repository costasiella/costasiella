# syntax=docker/dockerfile:1
FROM python:3.8

LABEL version="0.01"

# Get the latest & greatest
RUN apt-get update && \
    apt-get upgrade -y
    
RUN apt-get install -y libffi-dev libmariadb-dev

# Copy app into container
COPY ./docker-backend-entrypoint.sh /opt/
COPY ./docker-celery-entrypoint.sh /opt/
COPY ./docker-celery-beat-entrypoint.sh /opt/
COPY ./requirements.txt /opt/

# Install required packages
RUN pip install -r /opt/requirements.txt

# Create sockets directory
RUN mkdir /opt/sockets

# Create static files directory
RUN mkdir /opt/static

# Environment variables
ENV DJANGO_SETTINGS_MODULE=app.settings.production
ENV DJANO_LOG_LEVEL=WARNING

# Install uWSGI
RUN pip install uwsgi

RUN chmod a+x /opt/docker-backend-entrypoint.sh
RUN chmod a+x /opt/docker-celery-entrypoint.sh
RUN chmod a+x /opt/docker-celery-beat-entrypoint.sh
