# syntax=docker/dockerfile:1
FROM python:3.10-slim

LABEL version="0.03"

# Get the latest & greatest & install software
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libffi-dev libmariadb-dev build-essential && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Copy app into container
COPY ./app /opt/app
COPY ./docker/celery_beat/docker-celery-beat-entrypoint.sh /opt/
COPY ./requirements.txt /opt/

# Install required packages
RUN pip install --no-cache-dir -r /opt/requirements.txt

# Create sockets & static directory
RUN mkdir /opt/sockets && mkdir /opt/static

RUN chmod a+x /opt/docker-celery-beat-entrypoint.sh

CMD /opt/docker-celery-beat-entrypoint.sh
