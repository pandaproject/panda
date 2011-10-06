#!/usr/bin/env python

import logging
import os

class GroupWriteRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Rotating logger which also adds group+writable permissions.

    Tip from:
    http://stackoverflow.com/questions/1407474/does-python-logging-handlers-rotatingfilehandler-allow-creation-of-a-group-writab/6779307#6779307
    """
    def _open(self):
        old_umask = os.umask(0o002)
        f = logging.handlers.RotatingFileHandler._open(self)
        os.umask(old_umask)

        return f
