#!/usr/bin/env python

from django.conf import settings
from django.core.files.storage import FileSystemStorage

panda_storage = FileSystemStorage(location=settings.PANDA_STORAGE_LOCATION)

def save_ajax_upload(uploaded, filename, raw_data):
  ''' 
  raw_data: if True, uploaded is an HttpRequest object with the file being
            the raw post data 
            if False, uploaded has been submitted via the basic form
            submission and is a regular Django UploadedFile in request.FILES
  '''
  try:
    from io import FileIO, BufferedWriter
    with BufferedWriter( FileIO( filename, "wb" ) ) as dest:
      # if the "advanced" upload, read directly from the HTTP request 
      # with the Django 1.3 functionality
      if raw_data:
        foo = uploaded.read( 1024 )
        while foo:
          dest.write( foo )
          foo = uploaded.read( 1024 ) 
      # if not raw, it was a form upload so read in the normal Django chunks fashion
      else:
        for c in uploaded.chunks( ):
          dest.write( c )
      # got through saving the upload, report success
      return True
  except IOError:
    # could not open the file most likely
    pass
  return False
