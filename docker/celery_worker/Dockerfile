# syntax=docker/dockerfile:1
FROM python:3.10

LABEL version="0.03"

# Get the latest & greatest
RUN apt-get update && \
    apt-get upgrade -y
    
RUN apt-get install -y libffi-dev libmariadb-dev

# Copy app into container
COPY ./app /opt/app
COPY ./docker/celery_worker/docker-celery-entrypoint.sh /opt/
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

RUN chmod a+x /opt/docker-celery-entrypoint.sh

CMD /opt/docker-celery-entrypoint.sh