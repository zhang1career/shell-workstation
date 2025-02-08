#!/bin/bash

# set swap size 2GB by default
if [ $# -le 1 ]; then
	SWAP_SIZE = 2
else
	SWAP_SIZE = $1
fi


# the swap file is n x 1 GB (128 MB x 8 x n):
SWAP_COUNT = $((SWAP * 8))
sudo dd if=/dev/zero of=/swapfile bs=128M count=$SWAP_COUNT

# updating file permission
sudo chmod 600 /swapfile

# set up a Linux swap folder
sudo mkswap /swapfile

# add swap file to swap space to make it available for use
sudo swapon /swapfile

# verify taks is completed
sudo swapon -s

# start the swap file at boot time
echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab

