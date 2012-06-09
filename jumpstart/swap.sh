#!/usr/bin/bash

cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf
service uwsgi stop
initctl reload-configuration
service uwsgi start
