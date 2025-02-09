#!/bin/bash

# check param cardinality
if [ $# -lt 1 ]; then
	echo "Error: user is not specified."
	exit 1
fi

USER_GROUP=dev
USER=$1

# create group if not exists
sudo getent group $USER_GROUP || sudo groupadd $USER_GROUP

# add user to group
sudo usermod -a -G $USER_GROUP $USER

echo "Success: $USER added to $USER_GROUP."
