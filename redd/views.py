#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader

from redd.storage import PANDAUploadBackend

upload = AjaxFileUploader(backend=PANDAUploadBackend)

