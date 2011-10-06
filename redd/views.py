#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader

from redd.storage import PANDAUploadBackend

ajax_upload = AjaxFileUploader(backend=PANDAUploadBackend)

