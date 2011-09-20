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
wget -P /etc/apt/apt.conf.d $CONFIG_URL/10periodic
service unattended-upgrades restart

# Install required packages
apt-get install --yes git postgresql-8.4 python2.7-dev git\
    libxml2-dev libxml2 nginx build-essential\
    openjdk-6-jdk solr-jetty virtualenvwrapper
pip install uwsgi

# Setup uWSGI
adduser --system --no-create-home --disabled-login --disabled-password --group uwsgi
mkdir /var/run/uwsgi
chown uwsgi.uwsgi /var/run/uwsgi
wget -P /etc/init $CONFIG_URL/uwsgi.conf
initctl reload-configuration
service uwsgi start

# Setup nginx
wget -P /etc/nginx $CONFIG_URL/nginx.conf
service nginx restart

# Get code
mkdir /home/ubuntu/src
cd /home/ubuntu/src
git clone git://github.com/pandaproject/panda.git panda
mkvirtualenv -p python2.7 --no-site-packages panda
pip install -q -r panda/requirements.txt
python panda/manage.py syncdb --noinput

# Create database users
su postgres
echo "CREATE USER panda WITH PASSWORD 'panda';" | psql postgres
createdb -O panda panda
exit

wget -P /etc/init $CONFIG_URL/celeryd.conf
service celeryd start

