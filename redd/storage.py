#!/usr/bin/env python

from django.conf import settings
from django.core.files.storage import FileSystemStorage

panda_storage = FileSystemStorage(location=settings.PANDA_STORAGE_LOCATION)
