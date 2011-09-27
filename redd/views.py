#!/usr/bin/env python

from django.http import HttpResponse
from sunburnt import SolrInterface

from redd.forms import UploadForm
from redd.tasks import add 

def test_task(request):
    result = add.delay(4, 4)
    result.get()

    return HttpResponse(result.get())

def test_solr(request):
    solr = SolrInterface('http://localhost:8983')
    solr.add({ 'test': 'test' })
    solr.commit()

    return HttpResponse('Success')

def handle_uploaded_file(f):
    destination = open('some/file/name.txt', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def test_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
    else:
        form = UploadForm()

    return render_to_response('upload.html', {'form': form})

