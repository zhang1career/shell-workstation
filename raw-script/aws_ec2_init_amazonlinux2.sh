#!/bin/bash

sudo yum update –y

sudo yum upgrade

# htop
sudo yum -y install htop

# git
sudo yum -y install git

# java
sudo yum -y install java-17-amazon-corretto-devel

# zsh
sudo yum -y install zsh
# chsh
sudo yum -y install util-linux-user
# change default shell for current user
sudo chsh -s $(which zsh) $(whoami)

# mysql
sudo wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
sudo yum -y localinstall mysql57-community-release-el7-11.noarch.rpm 
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
sudo yum -y install mysql-community-server
sudo systemctl start mysqld.service
sudo systemctl enable mysqld.service


