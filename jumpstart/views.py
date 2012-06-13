#!/usr/bin/env python

import os
import subprocess
import time

from django.conf import settings
from django.shortcuts import render_to_response
from pytz import common_timezones

from daemon import Daemon

LOCAL_SETTINGS_PATH = '%s/local_settings.py' % settings.SITE_ROOT
RESTART_SCRIPT_PATH = '%s/jumpstart/restart-uwsgi.sh' % settings.SITE_ROOT 
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
    context = {
        'settings': settings,
        'timezones': common_timezones
    }

    return render_to_response('jumpstart/index.html', context)

def wait(request):
    timezone = request.POST['timezone']

    # Test if running under runserver
    # (Via: http://stackoverflow.com/questions/10962703/django-distinguish-development-server-manage-py-runserver-from-the-regular-o)
    wsgi_wrapper = request.META.get('wsgi.file_wrapper', None)
    wsgi_wrapper_path = wsgi_wrapper.__module__ if wsgi_wrapper else None

    with open(LOCAL_SETTINGS_PATH, 'w') as f:
        f.write("TIME_ZONE = '%s'\n" % timezone)

        if wsgi_wrapper_path:
            f.write("DEBUG = 'True'\n")

    if not wsgi_wrapper_path:
        daemon = RestartDaemon(DAEMON_PID_PATH, stdout=DAEMON_LOG_PATH)
        daemon.start()

    return render_to_response('jumpstart/wait.html', { 'settings': settings })

