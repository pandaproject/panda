#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import simplejson as json

from redd.api.utils import CustomApiKeyAuthentication
from redd.storage import PANDAUploadBackend

class SecureAjaxFileUploader(AjaxFileUploader):
    """
    A custom version of AjaxFileUploader that checks for authorization.
    """
    def __call__(self, request):
        auth = CustomApiKeyAuthentication()

        if auth.is_authenticated(request) != True:
            # Valum's FileUploader only parses the response if the status code is 200.
            return HttpResponse(json.dumps({ 'success': False, 'forbidden': True }), content_type='application/json', status=200)

        return self._ajax_upload(request)

upload = SecureAjaxFileUploader(backend=PANDAUploadBackend)

def panda_login(request):
    """
    PANDA login: takes a username and password and returns an API key
    for querying the API.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Success
                return HttpResponse(json.dumps({ 'username': user.username, 'api_key': user.api_key.key }), content_type='application/json')
            else:
                # Disabled account
                return HttpResponse(json.dumps({ 'message': 'Account is disabled' }), content_type='application/json', status=403)
        else:
            # Invalid login
            return HttpResponse(json.dumps({ 'message': 'Username or password is incorrect' }), content_type='application/json', status=400) 
    else:
        # Invalid request
        return HttpResponse('null', content_type='application/json', status=400)

def panda_register(request):
    """
    PANDA user registeration.
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return HttpResponse(json.dumps({ 'message': 'Username already in use' }), content_type='application/json', status=400)

        # Success
        return HttpResponse(json.dumps({ 'username': user.username, 'api_key': user.api_key.key }), content_type='application/json')
    else:
        # Invalid request
        return HttpResponse('null', content_type='application/json', status=400)

