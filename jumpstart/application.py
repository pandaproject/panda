#!/usr/bin/env python

import os
import subprocess
import time

from flask import Flask, render_template, request
from pytz import common_timezones

from daemon import Daemon

# Configuration
DEBUG = True
TEST_MODE = False

PANDA_PATH = '/opt/panda'
LOCAL_SETTINGS_PATH = '%s/local_settings.py' % PANDA_PATH
RESTART_SCRIPT_PATH = '%s/jumpstarts/restart-uwsgi.sh' % PANDA_PATH
DAEMON_PID_PATH = '/tmp/jumpstart-restart.pid'
DAEMON_LOG_PATH = '/var/log/jumpstart-restart.log'

# Setup
app = Flask(__name__)
app.debug = DEBUG

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timezone = request.form['timezone']

        if not TEST_MODE:
            with open(LOCAL_SETTINGS_PATH, 'w') as f:
                f.write("TIME_ZONE = '%s'\n" % timezone)

	        daemon = RestartDaemon(DAEMON_PID_PATH, stdout=DAEMON_LOG_PATH)
	        daemon.start()

        return render_template('wait.html')
    else:
        context = {
            'timezones': common_timezones
        }

        return render_template('index.html', **context)

if __name__ == '__main__':
    # When using Runserver, enable TEST_MODE 
    TEST_MODE = True

    app.run(host='0.0.0.0', port=8000)

