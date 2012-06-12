#!/usr/bin/env python

import os
import subprocess
import time

from django.shortcuts import render_to_response
from pytz import common_timezones

from daemon import Daemon

PANDA_PATH = '/opt/panda'
LOCAL_SETTINGS_PATH = '%s/local_settings.py' % PANDA_PATH
RESTART_SCRIPT_PATH = '%s/jumpstart/restart-uwsgi.sh' % PANDA_PATH
DAEMON_PID_PATH = '/tmp/jumpstart-restart.pid'
DAEMON_LOG_PATH = '/var/log/jumpstart-restart.log'

class RestartDaemon(Daemon):
    """
    Simple daemon so that a uwsgi process can reboot itself
    """
    def run(self):
        # Sleep for a moment to give uwsgi a chance to return a response
        time.sleep(5)

        subprocess.call(['sudo', RESTART_SCRIPT_PATH])
        
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

def jumpstart(request):
    if request.method == 'POST':
        timezone = request.POST['timezone']

        with open(LOCAL_SETTINGS_PATH, 'w') as f:
            f.write("TIME_ZONE = '%s'\n" % timezone)

        daemon = RestartDaemon(DAEMON_PID_PATH, stdout=DAEMON_LOG_PATH)
        daemon.start()

        return render_to_response('wait.html')
    else:
        context = {
            'timezones': common_timezones
        }

        return render_to_response('index.html', **context)

