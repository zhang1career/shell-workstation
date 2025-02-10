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

# nginx
sudo yum install -y nginx

# php
sudo yum -y install https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm
sudo yum -y install https://rpms.remirepo.net/enterprise/remi-release-7.rpm
# refer to: https://blog.remirepo.net/post/2022/06/10/PHP-8.2-as-Software-Collection
sudo yum-config-manager --enable remi-php82
sudo yum -y install php82
sudo yum install -y php82-php-mysql php82-php-pdo php82-php-cli php82-php-soap php82-php-bcmath php82-php-redis php82-php-json php82-php-dom

sudo mkdir -p /var/log/php-fpm && sudo chmod 755 /var/log/php-fpm
sudo mkdir -p /run/php-fpm && sudo chmod 755 /run/php-fpm
sudo cat '[Service]' >> /etc/systemd/system/php82-php-fpm.service.d/env.conf
sudo systemctl start php82-php-fpm
sudo systemctl enable php82-php-fpm

# php composer
sudo curl -sS https://getcomposer.org/installer | sudo php
sudo mv composer.phar /usr/local/bin/composer
sudo ln -s /usr/local/bin/composer /usr/bin/composer

# mysql
sudo wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
sudo yum -y localinstall mysql57-community-release-el7-11.noarch.rpm 
sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
sudo yum -y install mysql-community-server
sudo systemctl start mysqld.service
sudo systemctl enable mysqld.service

# redis
sudo amazon-linux-extras install redis6
sudo systemctl start redis
sudo systemctl enable redis

