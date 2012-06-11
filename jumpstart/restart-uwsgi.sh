#!/usr/bin/bash

service nginx stop
service uwsgi stop

cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf
initctl reload-configuration

service uwsgi start
service nginx start
