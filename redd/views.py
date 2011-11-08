#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils import simplejson as json

from redd.storage import PANDAUploadBackend

upload = AjaxFileUploader(backend=PANDAUploadBackend)

def panda_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Success
                return HttpResponse(json.dumps({ 'username': request.user.username, 'api_key': request.user.api_key.key }), content_type='application/json')
            else:
                # Disabled account
                return HttpResponse('null', content_type='application/json', status=403)
        else:
            # Invalid login
            return HttpResponse('null', content_type='application/json', status=400) 
    else:
        # Invalid request
        return HttpResponse('null', content_type='application/json', status=400)

