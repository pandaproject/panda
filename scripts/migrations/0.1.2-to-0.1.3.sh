#!/bin/bash

# PANDA Project migration script to ugprade version 0.1.2 to version 0.1.3.
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-upgrade-0.1.3.log) 2>&1

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
git checkout 0.1.3

# Update Python requirements
pip install -U -r requirements.txt

# Migrate database
sudo -u panda -E python manage.py migrate panda 0010 --noinput   # Migrate to new models
sudo -u panda -E python manage.py syncdb --noinput               # Create new permissions
sudo -u panda -E python manage.py migrate panda --noinput        # Finish data migrations 

# Regenerate assets
sudo -u panda -E python manage.py collectstatic --noinput

# Restart services
service solr start 
service uwsgi start
service nginx start
sudo service celeryd start

echo "PANDA upgrade complete."

