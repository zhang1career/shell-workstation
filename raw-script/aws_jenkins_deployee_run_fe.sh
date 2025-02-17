#!/bin/bash

echo "Launch frontend image..."

if [ $# -eq 0 ]; then
  if [ -z "$1" ]; then
      read -rp "server port (13001): " SERVER_PORT
      SERVER_PORT="${SERVER_PORT:-13001}"
  fi

  if [ -z "$2" ]; then
      read -rp "container port (3000): " CONTAINER_PORT
      CONTAINER_PORT="${CONTAINER_PORT:-3000}"
  fi

  if [ -z "$3" ]; then
      read -rp "docker account (zhang1career): " DOCKER_ACCOUNT
      DOCKER_ACCOUNT="${DOCKER_ACCOUNT:-zhang1career}"
  fi

  if [ -z "$4" ]; then
      read -rp "image name (data-analyzer-fe): " IMAGE
      IMAGE="${IMAGE:-data-analyzer-fe}"
  fi

  if [ -z "$5" ]; then
      read -rp "image version (latest): " VERSION
      VERSION="${VERSION:-latest}"
  fi
elif [ $# -eq 5 ]; then
  SERVER_PORT=$1
  CONTAINER_PORT=$2
  DOCKER_ACCOUNT=$3
  IMAGE=$4
  VERSION=$5
else
  echo "Usage: $0 [server-port container-port docker-account image version]"
  exit 1
fi
echo ""


echo "Specify the following parameters:"
echo "SERVER_PORT=${SERVER_PORT}"
echo "CONTAINER_PORT=${CONTAINER_PORT}"
echo "DOCKER_ACCOUNT=${DOCKER_ACCOUNT}"
echo "IMAGE=${IMAGE}"
echo "VERSION=${VERSION}"
DOCKER_REPO="$DOCKER_ACCOUNT"/"$IMAGE"
echo "DOCKER_REPO=${DOCKER_REPO}"
CONTAINER_NAME="$IMAGE"_"$VERSION"
echo "CONTAINER_NAME=${CONTAINER_NAME}"
echo ""


echo "Shut down old container..."
docker stop "$CONTAINER_NAME" && docker rm "$CONTAINER_NAME" && docker image rm "$DOCKER_REPO":"$VERSION"

echo "Load image..."
docker load -i /download/"$CONTAINER_NAME".tar

echo "Run container..."
docker run --restart unless-stopped --name "$CONTAINER_NAME" -p "$SERVER_PORT":"$CONTAINER_PORT" -d "$DOCKER_REPO":"$VERSION"

echo "Done."