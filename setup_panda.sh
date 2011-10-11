#!/bin/bash

# PANDA Project server setup script for Ubuntu 11.04
# Must be executed with sudo!

CONFIG_URL="https://raw.github.com/pandaproject/panda/master/setup_panda"

# Setup environment variables
echo "export DEPLOYMENT_TARGET=\"deployed\"" > /home/ubuntu/.bash_profile
export DEPLOYMENT_TARGET="deployed"

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
apt-get install --yes git postgresql-8.4 python2.7-dev git libxml2-dev libxml2 libxlt1.1 libxslt1-dev nginx build-essential openjdk-6-jdk python-virtualenv libpq-dev
pip install uwsgi

# Setup Solr + Jetty
wget http://mirror.uoregon.edu/apache//lucene/solr/3.3.0/apache-solr-3.3.0.tgz -O /opt/

cd /opt/
tar -xzf apache-solr-3.3.0.tgz
mv apache-solr-3.3.0 solr
cp -r solr/example solr/panda

rm panda/solr/solr.xml
wget $CONFIG_URL/schema.xml -O /opt/solr/panda/solr/conf/schema.xml
wget $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/conf/solrconfig.xml

adduser --system --no-create-home --disabled-login --disabled-password --group solr
chown -R solr:solr /opt/solr

touch /var/log/solr.log
chown solr:solr /var/log/solr.log

wget $CONFIG_URL/solr.conf -O /opt/solr/panda/solr/conf/solrconfig.xml
initctl reload-configuration
service solr start

# Setup uWSGI
adduser --system --no-create-home --disabled-login --disabled-password --group panda
mkdir /var/run/uwsgi
chown panda:panda /var/run/uwsgi
wget $CONFIG_URL/uwsgi.conf -O /etc/init/uwsgi.conf
initctl reload-configuration

# Setup nginx
wget $CONFIG_URL/nginx.conf -O /etc/nginx/nginx.conf
service nginx restart

# Setup Postgres
wget $CONFIG_URL/pg_hba.conf -O /etc/postgresql/8.4/main/pg_hba.conf
service postgresql restart

# Create database users
echo "CREATE USER panda WITH PASSWORD 'panda';" | sudo -u postgres psql postgres
sudo -u postgres createdb -O panda panda

# Get code (as normal user)
sudo -u ubuntu mkdir /home/ubuntu/src
cd /home/ubuntu/src
sudo -u ubuntu git clone git://github.com/pandaproject/panda.git panda
sudo -u ubuntu virtualenv -p python2.7 --no-site-packages /home/ubuntu/.virtualenvs/panda
cd /home/ubuntu/src/panda
sudo -u ubuntu /home/ubuntu/.virtualenvs/panda/bin/pip install -r requirements.txt
sudo -u ubuntu /home/ubuntu/.virtualenvs/panda/bin/python manage.py syncdb --noinput

# Setup panda directories 
mkdir /var/log/panda
chown panda:panda /var/log/panda

mkdir /mnt/panda
chown panda:panda /mnt/panda

mkdir /mnt/media
chown panda:panda /mnt/media

# Collect static assets
sudo -u panda /home/ubuntu/.virtualenvs/panda/bin/python manage.py collectstatic --noinput

# Start serving
service uwsgi start

# Celery
wget $CONFIG_URL/celeryd.conf -O /etc/init/celeryd.conf
initctl reload-configuration
service celeryd start

