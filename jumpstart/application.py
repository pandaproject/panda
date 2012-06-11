#!/usr/bin/env python

import os
import subprocess
import time

from flask import Flask, render_template, request
from pytz import common_timezones

from daemon import Daemon

# Configuration
DEBUG = True

PANDA_PATH = '/opt/panda'
LOCAL_SETTINGS_PATH = '%s/local_settings.py' % PANDA_PATH

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

        subprocess.call(['sudo', '/opt/panda/jumpstart/restart-uwsgi.sh'])
        
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timezone = request.form['timezone']

        with open(LOCAL_SETTINGS_PATH, 'w') as f:
            f.write("TIME_ZONE = '%s'\n" % timezone)

	    daemon = RestartDaemon('/tmp/jumpstart-restart.pid', stdout='/var/log/jumpstart-restart.log')
	    daemon.start()

        return render_template('wait.html')
    else:
        context = {
            'timezones': common_timezones
        }

        return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

