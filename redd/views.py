#!/usr/bin/env python

from ajaxuploader.views import AjaxFileUploader
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from tastypie.serializers import Serializer

from redd.api.notifications import NotificationResource
from redd.api.utils import CustomApiKeyAuthentication
from redd.storage import PANDAUploadBackend

class JSONResponse(HttpResponse):
    """
    A shortcut for an HTTPResponse containing data serialized as json.

    Note: Uses Tastypie's serializer to transparently support serializing bundles.
    """
    def __init__(self, contents, **kwargs):
        serializer = Serializer()

        super(JSONResponse, self).__init__(serializer.to_json(contents), content_type='application/json', **kwargs)
                
class SecureAjaxFileUploader(AjaxFileUploader):
    """
    A custom version of AjaxFileUploader that checks for authorization.
    """
    def __call__(self, request):
        auth = CustomApiKeyAuthentication()

        if auth.is_authenticated(request) != True:
            # Valum's FileUploader only parses the response if the status code is 200.
            return JSONResponse({ 'success': False, 'forbidden': True }, status=200)

        return self._ajax_upload(request)

upload = SecureAjaxFileUploader(backend=PANDAUploadBackend)

def make_user_login_response(user):
    """
    Generate a response to a login request.
    """
    nr = NotificationResource()

    notifications = user.notifications.filter(read_at__isnull=True)

    bundles = [nr.build_bundle(obj=n) for n in notifications]
    notifications = [nr.full_dehydrate(b) for b in bundles]

    return {
        'email': user.email,
        'api_key': user.api_key.key,
        'notifications': notifications
    }

def panda_login(request):
    """
    PANDA login: takes a username and password and returns an API key
    for querying the API.
    """
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email.lower(), password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                # Success
                return JSONResponse(make_user_login_response(user))
            else:
                # Disabled account
                return JSONResponse({ '__all__': 'This account is disabled' }, status=400)
        else:
            # Invalid login
            return JSONResponse({ '__all__': 'Email or password is incorrect' }, status=400)
    else:
        # Invalid request
        return JSONResponse(None, status=400)

