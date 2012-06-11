#!/bin/bash

service uwsgi stop
cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf
service uwsgi start
