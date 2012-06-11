#!/bin/bash

# PANDA Project migration script to ugprade version 0.1.4 to version 0.2.0.
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-upgrade-0.2.0.log) 2>&1

echo "PANDA upgrade beginning."

# Setup environment variables
export DEPLOYMENT_TARGET="deployed"

# Shutdown services
service celeryd stop
service nginx stop
service uwsgi stop
service solr stop

# Install outstanding updates
apt-get --yes update
apt-get --yes upgrade

# Fetch updated source code
cd /opt/panda
git pull
git checkout 0.2.0

# Update Python requirements
pip install -U -r requirements.txt

# Migrate database
sudo -u panda -E python manage.py migrate panda --noinput

# Regenerate assets
sudo -u panda -E python manage.py collectstatic --noinput

# Delete old cron script
rm /etc/cron.d/panda 

# Install updated celeryd upstart configuration
cp setup_panda/celeryd.conf -O /etc/init/celeryd.conf
initctl reload-configuration

# Create directory for celerybeat database
mkdir /var/celery
chown panda:panda /var/celery

# Install new Solr configuration (backwards compatible)
cp setup_panda/data_schema.xml /opt/solr/panda/solr/pandadata/conf/schema.xml
cp setup_panda/datasets_schema.xml /opt/solr/panda/solr/pandadatasets/conf/schema.xml

# Restart services
service solr start 
service uwsgi start
service nginx start
sudo service celeryd start

echo "PANDA upgrade complete."

