#!/usr/bin/env python

"""
Comprehensive script to handle backing up PANDA's EBS volumes.
"""

from datetime import datetime
from getpass import getpass
import os
import subprocess
import sys
import time

from boto.ec2.connection import EC2Connection
from boto.utils import get_instance_metadata

# Utilities
def safe_dismount(mount_point):
    dismounted = False

    while not dismounted:
        try:
            subprocess.check_output(['umount', mount_point], stderr=subprocess.STDOUT)
            dismounted = True
        except:
            time.sleep(1)

def mount_point_from_device_name(device):
    df = subprocess.check_output(['df', device])
    return df.split()[-1]

# Sanity checks
if not os.geteuid() == 0:
    sys.exit('You must run this script with sudo!')

metadata = get_instance_metadata()
instance_id = metadata['instance-id'] 

# Prompt for parameters
aws_key = getpass('Enter your AWS Access Key: ')
secret_key = getpass('Enter your AWS Secret Key: ')

print 'Beginning PANDA backup'

sys.stdout.write('Connecting to EC2... ')
conn = EC2Connection(aws_key, secret_key)
print 'connected'

sys.stdout.write('Identifying attached volumes...')
volumes = [v for v in conn.get_all_volumes() if v.attach_data.instance_id == instance_id]
print volumes

sys.stdout.write('Stopping services... ')
subprocess.check_output(['service', 'uwsgi', 'stop'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'celeryd', 'stop'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'nginx', 'stop'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'postgresql', 'stop'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'solr', 'stop'], stderr=subprocess.STDOUT)
print 'stopped'

for v in volumes:
    device = v.attach_data.device.replace('/dev/sd', '/dev/xvd')
    mount_point = mount_point_from_device_name(device)

    description = 'PANDA backup of %s mounted at %s (created at %s)' % (v.id, mount_point, datetime.today().isoformat(' '))
    
    sys.stdout.write('Creating snapshot of %s (%s)... ' % (v.id, mount_point))
    v.create_snapshot(description)

    snapshot = conn.get_all_snapshots(filters={ 'description': description})[0]

    while snapshot.status == 'pending':
        time.sleep(2)
        snapshot.update()

    print 'created'

sys.stdout.write('Restarting services... ')
subprocess.check_output(['service', 'solr', 'start'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'postgresql', 'start'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'nginx', 'start'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'celeryd', 'start'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'uwsgi', 'start'], stderr=subprocess.STDOUT)
print 'restarted'

print 'Done!'

