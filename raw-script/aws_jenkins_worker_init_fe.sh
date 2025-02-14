GIT_REPO=https://github.com/zhang1career/data-analyzer-fe.git
GIT_BRANCH=feature-deploy-20250208
DEST_HOST=172.31.1.239
DEST_PORT=13001
DEST_CRED=~/.ssh/ec2-user_aws_zhang_gateway.pem
CONTAINER_PORT=3000

OWNER=zhang1career
IMAGE=data-analyzer-fe
VERSION=latest


WORKROOT=/project
WORKSPACE=workspace


# login json-worker
# prepare workspace
cd $WORKROOT || exit 1
git clone ${GIT_REPO} -b ${GIT_BRANCH} --single-branch ${WORKSPACE} || exit 1
cd $WORKSPACE || exit 1

# prepare .env
AUTH_SECRET="/4lnIFLqgA8GTbDeZXsQohpHhSZtwFa4Qg80DtTovhI="
API_BASE_URL="http://www.risk-conquer.com/api"
echo "AUTH_SECRET=${AUTH_SECRET}
API_BASE_URL=${API_BASE_URL}
" > .env

DOCKER_REPO=${OWNER}/${IMAGE}

# build
docker build -t ${DOCKER_REPO} .

# test
docker run --name ${IMAGE} -p ${CONTAINER_PORT}:${CONTAINER_PORT} -d --rm ${DOCKER_REPO}
curl localhost:${CONTAINER_PORT}
# should got like:
# /auth/signin?callbackUrl=http%3A%2F%2F92faa2765d34%3A3000%2F

# zip image
docker save ${DOCKER_REPO} | tqdm --bytes --total $(docker image inspect ${DOCKER_REPO} --format='{{.Size}}') > ${IMAGE}.tar
# copy image
scp -i ${DEST_CRED} ${IMAGE}.tar ec2-user@${DEST_HOST}:/download/

# cleanup
docker stop ${IMAGE}


# login destination
# deploying machine
sudo docker load -i /download/${IMAGE}.tar

# launch
docker run --name ${IMAGE}_${VERSION} -p ${DEST_PORT}:${CONTAINER_PORT} -d ${DOCKER_REPO}:${VERSION}
