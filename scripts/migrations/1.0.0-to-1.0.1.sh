#!/bin/bash

# PANDA Project migration script to ugprade version 1.0.0 to version 1.0.1.
# Must be executed with sudo!

set -x
exec 1> >(tee /var/log/panda-upgrade-1.0.1.log) 2>&1

echo "PANDA upgrade beginning."

# Setup environment variables
export DEPLOYMENT_TARGET="deployed"

# Shutdown services
service celeryd stop
service nginx stop
service uwsgi stop
service solr stop

# Fetch updated source code
cd /opt/panda
git pull
git checkout 1.0.1

# Update Python requirements
pip install -U -r requirements.txt

# Migrate database
sudo -u panda -E python manage.py migrate panda --noinput

# Regenerate assets
sudo -u panda -E python manage.py collectstatic --noinput

# Restart services
service solr start 
service uwsgi start
service nginx start
sudo service celeryd start

echo "PANDA upgrade complete."

