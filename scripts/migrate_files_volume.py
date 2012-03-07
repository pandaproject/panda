#!/usr/bin/env python

"""
Comprehensive script to handle migrating PANDA's files (uploads and exports)
to a larger EBS volume.
Handles all stages of device creation, attachment, file movement, etc.
It will work whether the files are currently on another EBS or on local storage.

The only thing this script does not do is detach and destroy any old volume.
"""

from getpass import getpass
import os
import shutil
import string
import subprocess
import sys
import time
from datetime import datetime

from boto.ec2.connection import EC2Connection
from boto.utils import get_instance_metadata

TEMP_MOUNT_POINT = '/mnt/filesmigration'
PANDA_DIR = '/var/lib/panda'
FSTAB_BACKUP = '/etc/fstab.filesmigration.bak'

# Utilities
def safe_dismount(mount_point):
    dismounted = False

    while not dismounted:
        try:
            subprocess.check_output(['umount', mount_point], stderr=subprocess.STDOUT)
            dismounted = True
        except:
            time.sleep(1)

# Sanity checks
if not os.geteuid() == 0:
    sys.exit('You must run this script with sudo!')

metadata = get_instance_metadata()

backed_up = raw_input('Migrating your PANDA files is a complicated and potentially destructive operation. Have you backed up your data? (y/N): ')

if backed_up.lower() != 'y':
    sys.exit('Back up your data before running this script! Aborting.')

# Prompt for parameters
aws_key = getpass('Enter your AWS Access Key: ')
secret_key = getpass('Enter your AWS Secret Key: ')
size_gb = raw_input('How many GB would you like your new PANDA files volume to be? ')

print 'Beginning PANDA files migration'

sys.stdout.write('Connecting to EC2... ')
conn = EC2Connection(aws_key, secret_key)
print 'connected'

sys.stdout.write('Identifying running instance... ')
instance_id = metadata['instance-id'] 

reservations = conn.get_all_instances()

instance = None

for r in reservations:
    for i in r.instances:
        if i.id == instance_id:
            instance = i
            break

    if instance:
        break

if not instance:
    sys.exit('Unable to determine running instance! Aborting.')

print instance_id

sys.stdout.write('Creating new volume... ')
vol = conn.create_volume(size_gb, instance.placement)
conn.create_tags([vol.id], {'Name': 'PANDA Uploads volume %s' % datetime.now().strftime('%Y-%m-%d')})
print vol.id

sys.stdout.write('Backing up fstab... ')
shutil.copy2('/etc/fstab', FSTAB_BACKUP)
print FSTAB_BACKUP

sys.stdout.write('Finding an available device path... ')
ec2_device_name = None
device_path = None

for letter in string.lowercase[6:]:
    ec2_device_name = '/dev/sd%s' % letter
    device_path = '/dev/xvd%s' % letter

    if not os.path.exists(device_path):
        break

print device_path

sys.stdout.write('Attaching new volume... ')
vol.attach(instance.id, ec2_device_name) 

while not os.path.exists(device_path):
    time.sleep(1)
print 'attached'

sys.stdout.write('Formatting volume... ')
subprocess.check_output(['mkfs.ext3', device_path], stderr=subprocess.STDOUT)
print 'formatted'

sys.stdout.write('Creating temporary mount point... ')
if os.path.exists(TEMP_MOUNT_POINT):
    shutil.rmtree(TEMP_MOUNT_POINT)

os.mkdir(TEMP_MOUNT_POINT)
print TEMP_MOUNT_POINT

sys.stdout.write('Mounting volume... ')
subprocess.check_output(['mount', device_path, TEMP_MOUNT_POINT], stderr=subprocess.STDOUT)
print 'mounted' 

sys.stdout.write('Stopping services... ')
subprocess.check_output(['service', 'uwsgi', 'stop'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'celeryd', 'stop'], stderr=subprocess.STDOUT)
print 'stopped'

sys.stdout.write('Copying indexes... ')
names = os.listdir(PANDA_DIR)

for name in names:
    if name == 'lost+found':
        continue

    src_path = os.path.join(PANDA_DIR, name)
    dest_path = os.path.join(TEMP_MOUNT_POINT, name)

    if os.path.isdir(src_path):
        shutil.copytree(src_path, dest_path)
    else:
        shutil.copy2(src_path, dest_path)

print 'copied'

if os.path.ismount(PANDA_DIR):
    sys.stdout.write('Dismounting old storage device... ')
    safe_dismount(PANDA_DIR)
    print 'dismounted'

    sys.stdout.write('Removing device from fstab... ')
    new_fstab = subprocess.check_output(['grep', '-Ev', PANDA_DIR, '/etc/fstab'], stderr=subprocess.STDOUT)
    print 'removed'

    with open('/etc/fstab', 'w') as f:
        f.write(new_fstab)
else:
    sys.stdout.write('Removing old indexes... ')
    shutil.rmtree(PANDA_DIR)
    os.mkdir(PANDA_DIR)

    print 'removed'

sys.stdout.write('Dismounting from temporary mount point...')
safe_dismount(TEMP_MOUNT_POINT)
print 'dismounted'

sys.stdout.write('Remounting at final mount point... ')
subprocess.check_output(['mount', device_path, PANDA_DIR], stderr=subprocess.STDOUT)
print 'mounted'

sys.stdout.write('Reseting permissions... ')
subprocess.check_output(['chown', '-R', 'panda:panda', PANDA_DIR], stderr=subprocess.STDOUT)
print 'reset'

sys.stdout.write('Restarting services... ')
subprocess.check_output(['service', 'celeryd', 'start'], stderr=subprocess.STDOUT)
subprocess.check_output(['service', 'uwsgi', 'start'], stderr=subprocess.STDOUT)
print 'restarted'

sys.stdout.write('Configuring fstab... ')
with open('/etc/fstab', 'a') as f:
    f.write('\n%s\t%s\text3\tdefaults,noatime\t0\t0\n' % (device_path, PANDA_DIR))
print 'configured'

print 'Done!'

