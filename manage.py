#!/usr/bin/env python
import os
from django.core.management import execute_manager

if not os.environ.has_key("DJANGO_SETTINGS_MODULE"):
    if not os.environ.has_key("DEPLOYMENT_TARGET"):
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    else:
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.%s.settings" % os.environ["DEPLOYMENT_TARGET"]

settings_module = os.environ["DJANGO_SETTINGS_MODULE"]

try:
    settings = __import__(settings_module, globals(), locals(), ['settings'], -1)
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file '%s.py'.\n" % settings_module)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
