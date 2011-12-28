#!/bin/bash

# PANDA Project server setup script for Ubuntu 11.10
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
apt-get install --yes git postgresql python2.7-dev git libxml2-dev libxml2 libxslt1.1 libxslt1-dev nginx build-essential openjdk-6-jdk libpq-dev python-pip mercurial
pip install uwsgi

# Setup Solr + Jetty
wget http://mirror.uoregon.edu/apache//lucene/solr/3.4.0/apache-solr-3.4.0.tgz -O /opt/apache-solr-3.4.0.tgz

cd /opt
tar -xzf apache-solr-3.4.0.tgz
mv apache-solr-3.4.0 solr
cp -r solr/example solr/panda

wget $CONFIG_URL/solr.xml -O /opt/solr/panda/solr/solr.xml

mkdir /opt/solr/panda/solr/pandadata
mkdir /opt/solr/panda/solr/pandadata/conf
mkdir /opt/solr/panda/solr/pandadata/lib

wget $CONFIG_URL/data_schema.xml -O /opt/solr/panda/solr/pandadata/conf/schema.xml
wget $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadata/conf/solrconfig.xml
wget $CONFIG_URL/panda.jar -O /opt/solr/panda/solr/pandadata/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadata_test
mkdir /opt/solr/panda/solr/pandadata_test/conf
mkdir /opt/solr/panda/solr/pandadata_test/lib

wget $CONFIG_URL/data_schema.xml -O /opt/solr/panda/solr/pandadata_test/conf/schema.xml
wget $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadata_test/conf/solrconfig.xml
wget $CONFIG_URL/panda.jar -O /opt/solr/panda/solr/pandadata_test/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadatasets
mkdir /opt/solr/panda/solr/pandadatasets/conf

wget $CONFIG_URL/datasets_schema.xml -O /opt/solr/panda/solr/pandadatasets/conf/schema.xml
wget $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadatasets/conf/solrconfig.xml

mkdir /opt/solr/panda/solr/pandadatasets_test
mkdir /opt/solr/panda/solr/pandadatasets_test/conf

wget $CONFIG_URL/datasets_schema.xml -O /opt/solr/panda/solr/pandadatasets_test/conf/schema.xml
wget $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadatasets_test/conf/solrconfig.xml

adduser --system --no-create-home --disabled-login --disabled-password --group solr
chown -R solr:solr /opt/solr

touch /var/log/solr.log
chown solr:solr /var/log/solr.log

wget $CONFIG_URL/solr.conf -O /etc/init/solr.conf
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
initctl reload-configuration
service nginx restart

# Setup Postgres
wget $CONFIG_URL/pg_hba.conf -O /etc/postgresql/9.1/main/pg_hba.conf
service postgresql restart

# Create database users
echo "CREATE USER panda WITH PASSWORD 'panda';" | sudo -u postgres psql postgres
sudo -u postgres createdb -O panda panda

# Get code
cd /opt
git clone git://github.com/pandaproject/panda.git panda
cd /opt/panda
pip install -r requirements.txt

# Setup panda directories 
mkdir /var/log/panda
touch /var/log/panda/panda.log
chown -R panda:panda /var/log/panda

mkdir /mnt/panda
chown panda:panda /mnt/panda

mkdir /mnt/media
chown panda:panda /mnt/media

# Synchronize the database
sudo -u panda DEPLOYMENT_TARGET=deployed python manage.py syncdb --noinput

# Collect static assets
sudo -u panda DEPLOYMENT_TARGET=deployed python manage.py collectstatic --noinput

# Start serving
service uwsgi start

# Setup Celery
wget $CONFIG_URL/celeryd.conf -O /etc/init/celeryd.conf
initctl reload-configuration
service celeryd start

