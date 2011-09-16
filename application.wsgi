import os
import sys
import site

# Reordering the path code from http://code.google.com/p/modwsgi/wiki/VirtualEnvironments

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Look for Virtual Env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../virtualenvs/panda"))

# Add our Virtual Env
site.addsitedir(os.path.join(
    env_path,
    "lib/python%s/site-packages" % sys.version[:3]
))

# Add our project
sys.path.append(os.path.dirname(__file__))
# and the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

#redirecting stdout to stderr cuz geopy uses print statements
sys.stdout = sys.stderr

# Fire up the WSGI
import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

# We have to setup our own wsgi handler so we can grab environment
# variables from apache.
def application(environ, start_response):

    # Discover our settings file
    try:
        os.environ["DJANGO_SETTINGS_MODULE"] = environ["DJANGO_SETTINGS_MODULE"]
    except KeyError:
        try:
            os.environ["DJANGO_SETTINGS_MODULE"] = "config.%(DEPLOYMENT_TARGET)s.settings" % (environ)
        except KeyError:
           os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    
    return _application(environ, start_response)

