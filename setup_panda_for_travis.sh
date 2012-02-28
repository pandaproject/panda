#!/bin/bash

# PANDA Project server setup script for Travis CI service
# Must be executed with sudo!

# Travis starts with an active virtualenv
deactivate

echo "PANDA installation beginning."

CONFIG_URL="https://raw.github.com/pandaproject/panda/master/setup_panda"

# Setup environment variables
export DEPLOYMENT_TARGET="deployed"

# Install outstanding updates
apt-get --yes update
apt-get --yes upgrade

# Install required packages
apt-get install --yes git openssh-server postgresql python2.7-dev libxml2-dev libxml2 libxslt1.1 libxslt1-dev build-essential openjdk-6-jdk libpq-dev python-pip mercurial

# Setup Solr + Jetty
wget -nv http://mirror.uoregon.edu/apache//lucene/solr/3.4.0/apache-solr-3.4.0.tgz -O /opt/apache-solr-3.4.0.tgz

cd /opt
tar -xzf apache-solr-3.4.0.tgz
mv apache-solr-3.4.0 solr
cp -r solr/example solr/panda

wget -nv $CONFIG_URL/solr.xml -O /opt/solr/panda/solr/solr.xml

mkdir /opt/solr/panda/solr/pandadata
mkdir /opt/solr/panda/solr/pandadata/conf
mkdir /opt/solr/panda/solr/pandadata/lib

wget -nv $CONFIG_URL/data_schema.xml -O /opt/solr/panda/solr/pandadata/conf/schema.xml
wget -nv $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadata/conf/solrconfig.xml
wget -nv $CONFIG_URL/panda.jar -O /opt/solr/panda/solr/pandadata/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadata_test
mkdir /opt/solr/panda/solr/pandadata_test/conf
mkdir /opt/solr/panda/solr/pandadata_test/lib

wget -nv $CONFIG_URL/data_schema.xml -O /opt/solr/panda/solr/pandadata_test/conf/schema.xml
wget -nv $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadata_test/conf/solrconfig.xml
wget -nv $CONFIG_URL/panda.jar -O /opt/solr/panda/solr/pandadata_test/lib/panda.jar

mkdir /opt/solr/panda/solr/pandadatasets
mkdir /opt/solr/panda/solr/pandadatasets/conf

wget -nv $CONFIG_URL/datasets_schema.xml -O /opt/solr/panda/solr/pandadatasets/conf/schema.xml
wget -nv $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadatasets/conf/solrconfig.xml

mkdir /opt/solr/panda/solr/pandadatasets_test
mkdir /opt/solr/panda/solr/pandadatasets_test/conf

wget -nv $CONFIG_URL/datasets_schema.xml -O /opt/solr/panda/solr/pandadatasets_test/conf/schema.xml
wget -nv $CONFIG_URL/solrconfig.xml -O /opt/solr/panda/solr/pandadatasets_test/conf/solrconfig.xml

adduser --system --no-create-home --disabled-login --disabled-password --group solr
chown -R solr:solr /opt/solr

touch /var/log/solr.log
chown solr:solr /var/log/solr.log

wget -nv $CONFIG_URL/solr.conf -O /etc/init/solr.conf
initctl reload-configuration
service solr start

# Setup Postgres
wget -nv $CONFIG_URL/pg_hba.conf -O /etc/postgresql/8.4/main/pg_hba.conf
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

mkdir /var/lib/panda
mkdir /var/lib/panda/uploads
mkdir /var/lib/panda/exports
mkdir /var/lib/panda/media

chown -R panda:panda /var/lib/panda

# Synchronize the database
sudo -u panda -E python manage.py syncdb --noinput
sudo -u panda -E python manage.py migrate --noinput
sudo -u panda -E python manage.py loaddata panda/fixtures/init_panda.json

# Setup Celery
wget -nv $CONFIG_URL/celeryd.conf -O /etc/init/celeryd.conf
initctl reload-configuration
service celeryd start

echo "PANDA installation complete."

sudo -u panda -E python manage.py test panda
