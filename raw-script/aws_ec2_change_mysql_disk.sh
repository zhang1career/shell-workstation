#!/bin/bash

# stop service
sudo systemctl stop mysqld.service

# configre datadir=/db1/mysql
sudo vim /etc/my.cnf

# migrate data from local to mounted disk
sudo mv /var/lib/mysql /db1/
sudo chown -R mysql:mysql /db1/mysql

# create a symlink to the old location
sudo ln -s /db1/mysql /var/lib/mysql
sudo chown -R /var/lib/mysql

# start service
sudo systemctl start mysqld.service
