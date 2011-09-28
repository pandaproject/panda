#!/usr/bin/env python

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from sunburnt import SolrInterface

from redd.forms import UploadForm
from redd.models import Upload
from redd.storage import save_ajax_upload
from redd.tasks import add 

def test_task(request):
    result = add.delay(4, 4)
    result.get()

    return HttpResponse(result.get())

def test_solr(request):
    solr = SolrInterface('http://localhost:8983/solr')
    solr.add({
        'dataset_id': '1',
        'id': '1'
    })
    solr.commit()

    return HttpResponse('Success')

def test_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            Upload.objects.create(
                file=request.FILES['file']
            )
    else:
        form = UploadForm()

    return render_to_response('test_upload.html', RequestContext(request, { 'form': form }))

def ajax_upload(request):
  if request.method == "POST":    
    if request.is_ajax( ):
      # the file is stored raw in the request
      upload = request
      is_raw = True
      # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
      try:
        filename = request.GET[ 'qqfile' ]
      except KeyError: 
        return HttpResponseBadRequest( "AJAX request not valid" )
    # not an ajax upload, so it was the "basic" iframe version with submission via form
    else:
      is_raw = False
      if len( request.FILES ) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
        upload = request.FILES.values( )[ 0 ]
      else:
        raise Http404( "Bad Upload" )
      filename = upload.name
     
    # save the file
    success = save_ajax_upload( upload, filename, is_raw )
 
    # let Ajax Upload know whether we saved it or not
    import json
    ret_json = { 'success': success, }
    return HttpResponse( json.dumps( ret_json ) )

def upload(request):
    return render_to_response('upload.html', RequestContext(request, {})) 
