#!/usr/bin/env python

import os

def get_total_disk_space(p):
    """
    Calculate the total disk space of the device on which a given file path resides.
    """
    s = os.statvfs(p)
    return s.f_frsize * s.f_blocks   

def get_free_disk_space(p):
    """
    Returns the number of free bytes on the drive that ``p`` is on
    """
    s = os.statvfs(p)
    return s.f_frsize * s.f_bavail

