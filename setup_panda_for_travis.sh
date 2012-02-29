#!/bin/bash

# PANDA Project server setup script for Travis CI service
# Must be executed with sudo!

set -x

echo "PANDA installation beginning."

CONFIG_URL="https://raw.github.com/pandaproject/panda/master/setup_panda"

# Setup environment variables
export DEPLOYMENT_TARGET="travisci"

# Install required packages
apt-get install --yes libxml2-dev libxml2 libxslt1.1 libxslt1-dev build-essential openjdk-6-jdk mercurial

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

echo "PANDA installation complete."
