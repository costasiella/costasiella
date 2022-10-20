#!/bin/sh

export COSTASIELLA_VERSION=$1

# backend
docker manifest create \
simplycode/costasiella_backend:$COSTASIELLA_VERSION \
--amend simplycode/costasiella_backend:$COSTASIELLA_VERSION-amd64 \
--amend simplycode/costasiella_backend:$COSTASIELLA_VERSION-arm64v8

docker manifest push simplycode/costasiella_backend:$COSTASIELLA_VERSION

# celery beat
docker manifest create \
simplycode/costasiella_celery_beat:$COSTASIELLA_VERSION \
--amend simplycode/costasiella_celery_beat:$COSTASIELLA_VERSION-amd64 \
--amend simplycode/costasiella_celery_beat:$COSTASIELLA_VERSION-arm64v8

docker manifest push simplycode/costasiella_celery_beat:$COSTASIELLA_VERSION

# celery worker
docker manifest create \
simplycode/costasiella_celery_worker:$COSTASIELLA_VERSION \
--amend simplycode/costasiella_celery_worker:$COSTASIELLA_VERSION-amd64 \
--amend simplycode/costasiella_celery_worker:$COSTASIELLA_VERSION-arm64v8

docker manifest push simplycode/costasiella_celery_worker:$COSTASIELLA_VERSION
