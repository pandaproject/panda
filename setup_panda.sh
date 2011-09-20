#!/bin/bash

# PANDA Project server setup script for Ubuntu 11.04
# Must be executed with sudo!

CONFIG_URL="https://raw.github.com/pandaproject/panda/master/setup_panda"

# Setup environment variables
echo "export DEPLOYMENT_TARGET=\"staging\"" > /home/ubuntu/.bash_profile
export DEPLOYMENT_TARGET="staging"

# Make sure SSH comes up on reboot
ln -s /etc/init.d/ssh /etc/rc2.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc3.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc4.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc5.d/S20ssh

# Install outstanding updates
apt-get --yes update
apt-get --yes upgrade

# Configure unattended upgrades
wget $CONFIG_URL/10periodic -O /etc/apt/apt.conf.d/10periodic
service unattended-upgrades restart

# Install required packages
apt-get install --yes git postgresql-8.4 python2.7-dev git\
    libxml2-dev libxml2 nginx build-essential\
    openjdk-6-jdk solr-jetty virtualenv
pip install uwsgi

# Turn on Jetty
echo "NO_START=0" > /etc/default/jetty
initctl reload-configuration
service jetty restart

# Setup uWSGI
adduser --system --no-create-home --disabled-login --disabled-password --group uwsgi
mkdir /var/run/uwsgi
chown uwsgi.uwsgi /var/run/uwsgi
wget $CONFIG_URL/uwsgi.conf -O /etc/init/uwsgi.conf
initctl reload-configuration
service uwsgi start

# Setup nginx
wget $CONFIG_URL/nginx.conf -O /etc/nginx/nginx.conf
service nginx restart

# Get code
mkdir /home/ubuntu/src
cd /home/ubuntu/src
git clone git://github.com/pandaproject/panda.git panda
virtualenv -p python2.7 --no-site-packages /home/ubuntu/.virtualenvs/panda
pip install -q -r panda/requirements.txt
python panda/manage.py syncdb --noinput

# Create database users
echo "CREATE USER panda WITH PASSWORD 'panda';" | sudo -u postgres psql postgres
sudo -u postgres createdb -O panda panda

wget $CONFIG_URL/celeryd.conf -O /etc/init/celeryd.conf
initctl reload-configuration
service celeryd start

