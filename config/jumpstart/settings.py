#!/usr/bin/env python

from config.settings import *
from config.deployed.settings import *

# Running in jumpstart mode
# This means the app will have root access!
SETTINGS = 'jumpstart'

try:
    from local_settings import *
except ImportError:
    pass

