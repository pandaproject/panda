#!/bin/bash

# PANDA Project migration script to ugprade version 0.1.0 to version 0.1.1.
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-upgrade.log) 2>&1

echo "PANDA upgrade beginning."

# Setup environment variables
export DEPLOYMENT_TARGET="deployed"

# Install outstanding updates
apt-get --yes update
apt-get --yes upgrade

# Shutdown services
sudo service celeryd stop
sudo service nginx stop
sudo service uwsgi stop
sudo service solr stop

# Fetch updated source code
cd /opt/panda
git pull
git checkout 0.1.1

# Update Python requirements
sudo pip install -U -r requirements.txt

# Migrate database
sudo -u panda -E python manage.py syncdb --noinput
sudo -u panda -E python manage.py schemamigration --initial panda
sudo -u panda -E python manage.py migrate panda 0001 --fake
sudo -u panda -E python manage.py migrate panda

# Install new Solr configuration (backwards compatible)
cp setup_panda/data_schema.xml -O /opt/solr/panda/solr/pandadata/conf/schema.xml
cp setup_panda/datasets_schema.xml -O /opt/solr/panda/solr/pandadatasets/conf/schema.xml

# Restart services
sudo service solr start 
sudo service uwsgi start
sudo service nginx start
sudo service celeryd start

