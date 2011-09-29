#!/usr/bin/env python

from io import BufferedWriter, FileIO
import os

from ajaxuploader.backends.base import AbstractUploadBackend
from django.conf import settings

from redd.models import Upload

class PANDAUploadBackend(AbstractUploadBackend):
    """
    Customized upload backend to put files in PANDA_STORAGE_LOCATION.
    """
    def update_filename(self, request, filename):
        self._original_filename = filename

        filename = self._original_filename
        root, ext = os.path.splitext(self._original_filename)
        path = os.path.join(settings.PANDA_STORAGE_LOCATION, filename)

        i = 1

        while os.path.exists(path):
            filename = '%s%i%s' % (root, i, ext)
            path = os.path.join(settings.PANDA_STORAGE_LOCATION, filename)
            i += 1

        return filename 

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

        path = os.path.join(settings.PANDA_STORAGE_LOCATION, filename)
        size = os.path.getsize(path)

        upload = Upload.objects.create(
            filename=filename,
            original_filename=self._original_filename,
            size=size)

        return { 'id': upload.id }

