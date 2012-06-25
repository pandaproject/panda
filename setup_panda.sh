#!/bin/bash

# PANDA Project server setup script for Ubuntu 11.10
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-install.log) 2>&1

echo "PANDA installation beginning."

VERSION="1.0.0"
CONFIG_PATH="/opt/panda/setup_panda"

# Setup environment variables
echo "DEPLOYMENT_TARGET=\"deployed\"" >> /etc/environment
export DEPLOYMENT_TARGET="deployed"

# Install outstanding updates
apt-get --yes update
apt-get --yes upgrade

# Install required packages
apt-get install --yes git openssh-server postgresql python2.7-dev libxml2-dev libxml2 libxslt1.1 libxslt1-dev nginx build-essential openjdk-6-jdk libpq-dev python-pip mercurial
pip install uwsgi

# Make sure SSH comes up on reboot
ln -s /etc/init.d/ssh /etc/rc2.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc3.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc4.d/S20ssh
ln -s /etc/init.d/ssh /etc/rc5.d/S20ssh

# Setup Solr + Jetty
wget -nv http://mirror.uoregon.edu/apache//lucene/solr/3.4.0/apache-solr-3.4.0.tgz -O /opt/apache-solr-3.4.0.tgz

cd /opt
tar -xzf apache-solr-3.4.0.tgz
mv apache-solr-3.4.0 solr
cp -r solr/example solr/panda

# Get PANDA code
git clone git://github.com/pandaproject/panda.git panda
cd /opt/panda
git checkout $VERSION

# Configure unattended upgrades
cp $CONFIG_PATH/10periodic /etc/apt/apt.conf.d/10periodic
service unattended-upgrades restart

# Install Solr configuration
cp $CONFIG_PATH/solr.xml /opt/solr/panda/solr/solr.xml

mkdir /opt/solr/panda/solr/pandadata
mkdir /opt/solr/panda/solr/pandadata/conf
mkdir /opt/solr/panda/solr/pandadata/lib

cp $CONFIG_PATH/data_schema.xml /opt/solr/panda/solr/pandadata/conf/schema.xml
cp $CONFIG_PATH/english_names.txt /opt/solr/panda/solr/pandadata/conf/english_names.txt
cp $CONFIG_PATH/solrconfig.xml /opt/solr/panda/solr/pandadata/conf/solrconfig.xml
cp $CONFIG_PATH/panda.jar /opt/solr/panda/solr/pandadata/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadata_test
mkdir /opt/solr/panda/solr/pandadata_test/conf
mkdir /opt/solr/panda/solr/pandadata_test/lib

cp $CONFIG_PATH/data_schema.xml /opt/solr/panda/solr/pandadata_test/conf/schema.xml
cp $CONFIG_PATH/english_names.txt /opt/solr/panda/solr/pandadata_test/conf/english_names.txt
cp $CONFIG_PATH/solrconfig.xml /opt/solr/panda/solr/pandadata_test/conf/solrconfig.xml
cp $CONFIG_PATH/panda.jar /opt/solr/panda/solr/pandadata_test/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadatasets
mkdir /opt/solr/panda/solr/pandadatasets/conf

cp $CONFIG_PATH/datasets_schema.xml /opt/solr/panda/solr/pandadatasets/conf/schema.xml
cp $CONFIG_PATH/solrconfig.xml /opt/solr/panda/solr/pandadatasets/conf/solrconfig.xml

mkdir /opt/solr/panda/solr/pandadatasets_test
mkdir /opt/solr/panda/solr/pandadatasets_test/conf

cp $CONFIG_PATH/datasets_schema.xml /opt/solr/panda/solr/pandadatasets_test/conf/schema.xml
cp $CONFIG_PATH/solrconfig.xml /opt/solr/panda/solr/pandadatasets_test/conf/solrconfig.xml

adduser --system --no-create-home --disabled-login --disabled-password --group solr
chown -R solr:solr /opt/solr

touch /var/log/solr.log
chown solr:solr /var/log/solr.log

cp $CONFIG_PATH/solr.conf /etc/init/solr.conf
initctl reload-configuration
service solr start

# Setup uWSGI
adduser --system --no-create-home --disabled-login --disabled-password --group panda
cp $CONFIG_PATH/uwsgi_jumpstart.conf /etc/init/uwsgi.conf
initctl reload-configuration

# Setup nginx
cp $CONFIG_PATH/nginx /etc/nginx/sites-available/panda
ln -s /etc/nginx/sites-available/panda /etc/nginx/sites-enabled/panda
rm /etc/nginx/sites-enabled/default
service nginx restart

# Setup Postgres
cp $CONFIG_PATH/pg_hba.conf /etc/postgresql/9.1/main/pg_hba.conf
service postgresql restart

# Create database users
echo "CREATE USER panda WITH PASSWORD 'panda';" | sudo -u postgres psql postgres
sudo -u postgres createdb -O panda panda

# Install Python requirements
pip install -r requirements.txt

# Setup panda directories 
mkdir /var/log/panda
touch /var/log/panda/panda.log
chown -R panda:panda /var/log/panda

mkdir /var/lib/panda
mkdir /var/lib/panda/uploads
mkdir /var/lib/panda/exports
mkdir /var/lib/panda/media

chown -R panda:panda /var/lib/panda

# Synchronize the database
sudo -u panda -E python manage.py syncdb --noinput
sudo -u panda -E python manage.py migrate --noinput
sudo -u panda -E python manage.py loaddata panda/fixtures/init_panda.json

# Collect static assets
sudo -u panda -E python manage.py collectstatic --noinput

# Start serving
service uwsgi start

# Setup Celery
cp $CONFIG_PATH/celeryd.conf /etc/init/celeryd.conf
initctl reload-configuration
mkdir /var/celery
chown panda:panda /var/celery
service celeryd start

echo "PANDA installation complete."

