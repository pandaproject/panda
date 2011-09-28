#!/usr/bin/env python

from io import BufferedWriter, FileIO
import os

from ajaxuploader.backends.base import AbstractUploadBackend
from django.conf import settings
from django.core.files.storage import FileSystemStorage

panda_storage = FileSystemStorage(location=settings.PANDA_STORAGE_LOCATION)

class PANDAUploadBackend(AbstractUploadBackend):
    """
    Customized upload backend to put files in PANDA_STORAGE_LOCATION.
    """
    def setup(self, filename):
        self._path = os.path.join(settings.PANDA_STORAGE_LOCATION, filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._dest = BufferedWriter(FileIO(self._path, "w"))

    def upload_chunk(self, chunk):
        self._dest.write(chunk)

    def upload_complete(self, request, filename):
        self._dest.close()
        return { 'path': self._path }

