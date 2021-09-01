# syntax=docker/dockerfile:1
FROM python:3.8

LABEL version="0.01"
 

# Get the latest & greatest
RUN apt-get update && \
    apt-get install -y
    
RUN apt-get install libffi-dev libmariadb-dev

# Copy app into container
COPY ./app /opt/costasiella/app	
COPY ./docker-entrypoint.sh /opt/costasiella/
COPY ./requirements.txt /opt/costasiella/

# Install required packages
RUN pip install -r /opt/costasiella/requirements.txt

# Create sockets directory
RUN mkdir /opt/sockets

# Create static files directory
RUN mkdir /opt/static

# Environment variables
ENV DJANGO_SETTINGS_MODULE=app.settings.production

# Collect static files
# RUN cd /opt/costasiella/app && python manage.py collectstatic --no-input

# DB migrations
# RUN cd /opt/costasiella/app && python manage.py migrate --no-input

# Install uWSGI
RUN pip install uwsgi

# Which uWSGI .ini file should be used, to make it customizable
#CMD ["uwsgi", "--ini", "/opt/costasiella/app/deploy/app_uwsgi.ini"]

RUN chmod a+x /opt/costasiella/docker-entrypoint.sh
ENTRYPOINT [ "/opt/costasiella/docker-entrypoint.sh" ]
