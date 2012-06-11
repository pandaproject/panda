#!/usr/bin/env python

import subprocess

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
    # Simple daemon so that a uwsgi process can reboot itself
    def run(self):
        subprocess.Popen(['sudo', '/opt/panda/jumpstart/restart-uwsgi.sh'])
        self.stop()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timezone = request.form['timezone']

        with open(LOCAL_SETTINGS_PATH, 'w') as f:
            f.write("TIME_ZONE = '%s'\n" % timezone)

	    daemon = RestartDaemon('/tmp/restart.pid')
	    daemon.start()

        # Execution never reaches this point
        return 'Reloading!'
    else:
        context = {
            'timezones': common_timezones
        }

        return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

