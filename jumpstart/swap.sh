#!/usr/bin/bash

set -x
exec 1> >(tee /tmp/jumpstart.log) 2>&1

echo "1" > /tmp/foo.txt
cp /opt/panda/setup_panda/uwsgi.conf /etc/init/uwsgi.conf

echo "2" >> /tmp/foo.txt
service uwsgi stop
echo "3" >> /tmp/foo.txt
initctl reload-configuration
echo "4" >> /tmp/foo.txt
service uwsgi start
echo "5" >> /tmp/foo.txt
