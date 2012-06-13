#!/usr/bin/env python

from config.settings import *
from config.deployed.settings import *

# Running in jumpstart mode
# This means the app will have root access!
SETTINGS = 'jumpstart'

DAEMON_PID_PATH = '/tmp/jumpstart-restart.pid'
DAEMON_LOG_PATH = '/var/log/jumpstart-restart.log'

try:
    from local_settings import *
except ImportError:
    pass

