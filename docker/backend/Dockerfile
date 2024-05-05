# syntax=docker/dockerfile:1
FROM python:3.12-slim

LABEL version="0.03"

# Get the latest & greatest & install software
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libffi-dev libmariadb-dev  libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 build-essential && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Copy app into container
COPY ./app /opt/app
COPY ./docker/backend/docker-backend-entrypoint.sh /opt/
COPY ./requirements.txt /opt/

# Install required packages
RUN pip install --no-cache-dir -r /opt/requirements.txt && \
	pip install --no-cache-dir uwsgi

# Create sockets & static directory
RUN mkdir /opt/sockets && \
	mkdir /opt/static && \
	chmod a+x /opt/docker-backend-entrypoint.sh

CMD /opt/docker-backend-entrypoint.sh
