#!/usr/bin/bash

sudo cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf
sudo service uwsgi stop
sudo initctl reload-configuration
sudo service uwsgi start
