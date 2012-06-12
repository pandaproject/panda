#!/bin/bash

cd /opt/panda

service uwsgi stop
cp setup_panda/uwsgi.conf /etc/init/uwsgi.conf

DEPLOYMENT_TARGET="deployed" python manage.py collectstatic --noinput

service uwsgi start
