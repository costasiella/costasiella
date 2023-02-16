# syntax=docker/dockerfile:1
FROM python:3.10

LABEL version="0.03"

# Get the latest & greatest
RUN apt-get update && \
    apt-get upgrade -y
    
RUN apt-get install -y libffi-dev libmariadb-dev

# Copy app into container
COPY ./app /opt/app
COPY ./docker/celery_beat/docker-celery-beat-entrypoint.sh /opt/
COPY ./requirements.txt /opt/

# Install required packages
RUN pip install -r /opt/requirements.txt

# Create sockets directory
RUN mkdir /opt/sockets

# Create static files directory
RUN mkdir /opt/static

RUN chmod a+x /opt/docker-celery-beat-entrypoint.sh

CMD /opt/docker-celery-beat-entrypoint.sh
