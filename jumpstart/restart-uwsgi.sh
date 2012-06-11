#!/bin/bash

sudo service nginx stop
sudo service uwsgi stop

sudo cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf
sudo initctl reload-configuration

sudo service uwsgi start
sudo service nginx start
