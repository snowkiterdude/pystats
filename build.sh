#!/bin/bash

if [[ $(uname -m) != 'arm64' ]]; then
  echo "arm64 builder required"
  exit 1
fi

IMAGE="snowkiterdude/pystats"
VERSION="v0.0.3"
if [ "${1}" = "amd64" ]; then
    IMAGE_NAME="${IMAGE}:amd64-${VERSION}"
    docker build --platform linux/amd64 -t "${IMAGE_NAME}" .
    docker tag "${IMAGE_NAME}" "${IMAGE}:latest"
else
    IMAGE_NAME="${IMAGE}:arm64-${VERSION}"
    docker buildx build -t "${IMAGE_NAME}" .
fi
echo "${IMAGE_NAME}"
