#!/bin/bash

echo "Build frontend image..."

if [ $# -eq 0 ]; then
  if [ -z "$1" ]; then
      read -rp "git repository (https://github.com/zhang1career/data-analyzer-fe.git): " GIT_REPO
      GIT_REPO="${GIT_REPO:-https://github.com/zhang1career/data-analyzer-fe.git}"
  fi

  if [ -z "$2" ]; then
      read -rp "git branch name (master): " GIT_BRANCH
      GIT_BRANCH="${GIT_BRANCH:-master}"
  fi

  if [ -z "$3" ]; then
      read -rp "deploying host (172.31.1.239): " DEST_HOST
      DEST_HOST="${DEST_HOST:-172.31.1.239}"
  fi

  if [ -z "$4" ]; then
      read -rp "image name (data-analyzer-fe): " IMAGE
      IMAGE="${IMAGE:-data-analyzer-fe}"
  fi

  if [ -z "$5" ]; then
      read -rp "image version (latest): " VERSION
      VERSION="${VERSION:-latest}"
  fi

  if [ -z "$6" ]; then
      read -rp "home url (http://www.risk-conquer.com:13001): " HOME_URL
      HOME_URL="${HOME_URL:-http://www.risk-conquer.com:13001}"
  fi

  if [ -z "$7" ]; then
      read -rp "api-base url (http://www.risk-conquer.com/api): " API_BASE_URL
      API_BASE_URL="${API_BASE_URL:-http://www.risk-conquer.com/api}"
  fi
elif [ $# -eq 7 ]; then
  GIT_REPO=$1
  GIT_BRANCH=$2
  DEST_HOST=$3
  IMAGE=$4
  VERSION=$5
  HOME_URL=$6
  API_BASE_URL=$7
else
  echo "Usage: $0 [git-repo git-branch dest-host image version home-url api-base-url]"
  exit 1
fi
echo ""


echo "Specify the following parameters:"

echo "GIT_REPO=${GIT_REPO}"
echo "GIT_BRANCH=${GIT_BRANCH}"
echo "DEST_HOST=${DEST_HOST}"

DEST_CRED=~/.ssh/ec2-user_aws_zhang_gateway.pem
echo "DEST_CRED=${DEST_CRED}"

CONTAINER_PORT=3000
echo "CONTAINER_PORT=${CONTAINER_PORT}"

OWNER=zhang1career
echo "OWNER=${OWNER}"

echo "IMAGE=${IMAGE}"
echo "VERSION=${VERSION}"
DOCKER_REPO=${OWNER}/${IMAGE}
echo "DOCKER_REPO=${DOCKER_REPO}"

WORK_ROOT=/project
echo "WORK_ROOT=${WORK_ROOT}"
WORKSPACE=workspace
echo "WORKSPACE=${WORKSPACE}"

echo "HOME_URL=${HOME_URL}"

AUTH_SECRET="/4lnIFLqgA8GTbDeZXsQohpHhSZtwFa4Qg80DtTovhI="
echo "API_BASE_URL=${API_BASE_URL}"
echo ""


echo "Prepare..."

# prepare workspace
cd $WORK_ROOT || exit 1
git clone "$GIT_REPO" -b "$GIT_BRANCH" --single-branch "$WORKSPACE" || exit 1
cd $WORKSPACE || exit 1

# prepare .env
echo "AUTH_SECRET=${AUTH_SECRET}
AUTH_TRUST_HOST=true
AUTH_URL=${HOME_URL}
API_BASE_URL=${API_BASE_URL}
" > .env


echo "Build..."

# build
docker build -t "$DOCKER_REPO" .


echo "Test..."

# test
docker run --name "$IMAGE" -p "$CONTAINER_PORT":"$CONTAINER_PORT" -d "$DOCKER_REPO"
curl localhost:"$CONTAINER_PORT"
# should got like:
# /auth/signin?callbackUrl=http%3A%2F%2F92faa2765d34%3A3000%2F


echo "Deploy..."
# zip image
docker save "$DOCKER_REPO" | tqdm --bytes --total "$(docker image inspect $DOCKER_REPO --format='{{.Size}}')" > "$IMAGE"_"$VERSION".tar
# copy image
scp -i ${DEST_CRED} "$IMAGE"_"$VERSION".tar ec2-user@"$DEST_HOST":/download/


echo "Cleanup..."

# cleanup
docker stop "$IMAGE"