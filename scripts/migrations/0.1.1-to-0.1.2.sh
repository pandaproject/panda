#!/bin/bash

# PANDA Project migration script to ugprade version 0.1.1 to version 0.1.2.
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-upgrade.log) 2>&1

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
git checkout 0.1.2

# Update Python requirements
pip install -U -r requirements.txt

# Migrate database
sudo -u panda -E python manage.py migrate panda
sudo -u panda -E python manage.py migrate djcelery 0001 --fake
sudo -u panda -E python manage.py migrate djcelery

# Regenerate asset
sudo -u panda -E python manage.py collectstatic --noinput

# Install new Solr startup script
cp setup_panda/solr.conf /etc/init/solr.conf

# Restart services
service solr start 
service uwsgi start
service nginx start
sudo service celeryd start

echo "PANDA upgrade complete."

