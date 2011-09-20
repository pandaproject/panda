#!/bin/bash

# PANDA Project server setup script for Ubuntu 11.04
# Must be executed with sudo!

# Setup environment variables
#TODO: vim /home/ubuntu/.bash_profile 
source /home/ubuntu/.bash_profile

# Make sure SSH comes up on reboot
ln -s /etc/init.d/ssh /etc/rc2.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc3.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc4.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc5.d/S20ssh

# Install outstanding updates
apt-get update
apt-get upgrade

# Configure unattended upgrades
#TODO: vim /etc/apt/apt.conf.d/10periodic
service unattended-upgrades restart

# Install required packages
apt-get install git postgresql-8.4 python2.7-dev git libxml2-dev libxml2 nginx build-essential virtualenvwrapper openjdk-6-jdk solr-jetty
pip install uwsgi

# Setup uwsgi
adduser --system --no-create-home --disabled-login --disabled-password --group uwsgi
mkdir /var/run/uwsgi
chown uwsgi.uwsgi /var/run/uwsgi
#TODO: vim /etc/init/uwsgi.conf
initctl reload-configuration
service uwsgi start

# Setup nginx
#TODO: vim /etc/nginx/nginx.conf
service nginx restart

# Create a directory for code
mkdir /home/ubuntu/src

# NEED CODE HERE

#TODO: vim /etc/init/celeryd.conf
service celeryd start

# Now ready to deploy with fabric

