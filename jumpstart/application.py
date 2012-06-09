#!/usr/bin/env python

import subprocess

from pytz import common_timezones

from flask import Flask, render_template, request

# Configuration
DEBUG = True

PANDA_PATH = '/opt/panda'
LOCAL_SETTINGS_PATH = '%s/local_settings.py' % PANDA_PATH

# Setup
app = Flask(__name__)
app.debug = DEBUG

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timezone = request.form['timezone']

        with open(LOCAL_SETTINGS_PATH, 'w') as f:
            f.write("TIME_ZONE = '%s'\n" % timezone)

        subprocess.Popen(['bash', 'swap.sh'], shell=True)

        return 'Reload me!'
    else:
        context = {
            'timezones': common_timezones
        }

        return render_template('index.html', **context)

if __name__ == '__main__':
    app.run()

