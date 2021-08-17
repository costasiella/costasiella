# syntax=docker/dockerfile:1
FROM python:3.8

LABEL version="0.01"

# Get the latest & greatest
RUN apt-get update && \
    apt-get install -y
    
RUN apt-get install libffi-dev libmariadb-dev

# Copy app into container
COPY ./app /opt/costasiella/app	
COPY ./requirements.txt /opt/costasiella/

# Install required packages
RUN pip install -r /opt/costasiella/requirements.txt

# Install uWSGI
RUN pip install uwsgi

# Create sockets directory
RUN mkdir /opt/sockets

# Expose port 80
# EXPOSE 80

# Which uWSGI .ini file should be used, to make it customizable
CMD ["uwsgi", "--ini", "/opt/costasiella/app/deploy/app_uwsgi.ini"]
