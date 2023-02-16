#!/bin/sh

# check if $1 is set, if not exit requesting user to run it again and set it

export COSTASIELLA_VERSION=$1
export BUILD_ARCH=arm64v8

docker compose -f docker-compose-build.yml build --no-cache --build-arg ARCH=$BUILD_ARCH/
