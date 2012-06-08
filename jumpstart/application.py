#!/usr/bin/env python

import shutil
import subprocess

from pytz import common_timezones

from flask import Flask, render_template, request

# Configuration
DEBUG = True

PANDA_PATH = '/opt/panda'
UWSGI_CONF_SRC_PATH = '%s/setup_panda/uwsgi.conf' % PANDA_PATH
UWSGI_CONF_DEST_PATH = '/etc/init/uwsgi.conf'
LOCAL_SETTINGS_PATH = '%s/local_settings.py' % PANDA_PATH

# Setup
app = Flask(__name__)
app.debug = DEBUG

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        timezone = request.form['timezone']

        app.logger.debug('1')
        with open(LOCAL_SETTINGS_PATH, 'w') as f:
            f.write("TIME_ZONE = '%s'\n" % timezone)

        app.logger.debug('2')
        shutil.copy(UWSGI_CONF_SRC_PATH, UWSGI_CONF_DEST_PATH)
        app.logger.debug('3')
        subprocess.call(['initctl', 'reload-configuration'])
        app.logger.debug('4')
        subprocess.call(['service', 'uwsgi', '--full-restart'])
        app.logger.debug('5')

        return ''
    else:
        context = {
            'timezones': common_timezones
        }

        return render_template('index.html', **context)

if __name__ == '__main__':
    app.run()

