# ss
alias proxy_on='export http_proxy=http://127.0.0.1:1087 https_proxy=http://127.0.0.1:1087'
alias proxy_off='unset http_proxy https_proxy'


# docker
alias di="docker images"
alias dps="docker ps -a"
alias dpull="docker pull"
alias dstart="docker start"
alias dstop="docker stop"
alias drestart="docker restart"
alias dnls="docker network ls"

drun()  { docker run -itd $@; }
deit()  { docker exec -it $@ $(which bash) --login; }
dpause() { docker pause $@; }
dupause() { docker unpause $@; }
dlog()  { docker logs --tail=all -f $@; }
dport() { docker port $@; }
dvol()  { docker inspect --format '{{ .Volumes }}' $@; }
dip()   { docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $@; }
drmc()  { docker rm `docker ps -qa --filter 'status=exited'`; }
drmi()  { docker rmi -f `docker images | grep '^<none>' | awk '{print $3}'`; }
ddo()   {
   if [ "$#" -ne 1 ]; then
      echo "Usage: $0 start|stop|pause|unpause|<any valid docker cmd>"
   fi
   for c in $(docker ps -a | awk '{print $1}' | sed "1 d")
   do
       docker $1 $c
   done
}
ddpush() {
    # Check if two arguments are passed
    if [ "$#" -ne 3 ]; then
        echo "Usage: ddpush <container-hash-or-name> <repo-name> <version>"
        return 1
    fi

    local CONTAINER_ID=$1
    local REPO=$2
    local VERSION=$3
    local DOCKER_REPO="zhang1career/$REPO"

    echo "Committing container $CONTAINER_ID to image $DOCKER_REPO:$VERSION..."
    docker commit "$CONTAINER_ID" "$DOCKER_REPO:$VERSION" || {
        echo "Error: Failed to commit container."
        return 1
    }

    echo "Tagging image $DOCKER_REPO:$VERSION to repository $DOCKER_REPO:$VERSION..."
    docker tag "$DOCKER_REPO:$VERSION" "$DOCKER_REPO:$VERSION" || {
        echo "Error: Failed to tag image."
        return 1
    }

    echo "Pushing image $DOCKER_REPO:$VERSION to Docker Hub..."
    docker push "$DOCKER_REPO:$VERSION" || {
        echo "Error: Failed to push image."
        return 1
    }

    echo "Image $DOCKER_REPO:$VERSION has been pushed successfully!"
}


# docker-compose
dcps()  { docker-compose -f docker-compose.yml ps $@; }
dcup()  { docker-compose -f docker-compose.yml up -d $@; }
dcub()  { docker-compose -f docker-compose.yml up --build; }


##########
# utils
##########
sha256() {echo -n $1 | openssl dgst -sha256}


##########
# tools
##########
# dubbo
alias dubbo_admin="java -jar $TOOLS_HOME/dubbo-admin/dubbo-admin/target/dubbo-admin-0.0.1-SNAPSHOT.jar"

# java
# test
alias jmeter="/bin/sh $TOOLS_HOME/apache-jmeter-5.4.1/bin/jmeter"

# heidisql
alias heidi="wine64 $TOOLS_HOME/HeidiSQL/heidisql.exe"


##########
# operations
##########
# aliyun
alias ali_root="ssh -i ~/.ssh/root_ali_zhang_service root@47.93.157.39"
ali_up() { scp -i ~/.ssh/root_ali_zhang_service -r $1 root@47.93.157.39:$2; }
ali_down() { scp -i ~/.ssh/root_ali_zhang_service -r root@47.93.157.39:$1 $2; }
alias ali_redis="redis-cli -h 47.93.157.39 -p 16379 -a 'g00seisland!p@'"
