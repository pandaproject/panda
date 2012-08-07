#!/usr/bin/env python

import os

from ajaxuploader.views import AjaxFileUploader
from csvkit.exceptions import FieldSizeLimitError
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.timezone import now
from livesettings import config_value
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer

from client.utils import get_free_disk_space
from panda.api.notifications import NotificationResource
from panda.api.users import UserValidation
from panda.api.utils import PandaAuthentication
from panda.models import UserProfile, UserProxy
from panda.storage import PANDADataUploadBackend, PANDARelatedUploadBackend
from panda.utils.mail import send_mail

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
        auth = PandaAuthentication()

        if auth.is_authenticated(request) != True:
            # Valum's FileUploader only parses the response if the status code is 200.
            return JSONResponse({ 'success': False, 'forbidden': True }, status=200)

        try:
            return self._ajax_upload(request)
        except FieldSizeLimitError:
            return JSONResponse({ 'error_message': 'CSV contains fields longer than maximum length of 131072 characters.' })
        except Exception, e:
            return JSONResponse({ 'error_message': unicode(e) })

data_upload = SecureAjaxFileUploader(backend=PANDADataUploadBackend)
related_upload = SecureAjaxFileUploader(backend=PANDARelatedUploadBackend)

def make_user_login_response(user):
    """
    Generate a response to a login request.
    """
    nr = NotificationResource()

    notifications = user.notifications.all()[:settings.PANDA_NOTIFICATIONS_TO_SHOW]

    bundles = [nr.build_bundle(obj=n) for n in notifications]
    notifications = [nr.full_dehydrate(b) for b in bundles]

    return {
        'id': user.id,
        'email': user.email,
        'is_staff': user.is_staff,
        'show_login_help': user.get_profile().show_login_help,
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
            # Convert authenticated user to a proxy model
            _user_proxy = UserProxy()
            _user_proxy.__dict__ = user.__dict__
            user = _user_proxy

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

def check_activation_key(request, activation_key):
    """
    Test if an activation key is valid and if so fetch information
    about the user to populate the form.
    """
    try:
        user_profile = UserProfile.objects.get(activation_key=activation_key)
    except UserProfile.DoesNotExist:
        return JSONResponse({ '__all__': 'Invalid activation key' }, status=400)

    user = user_profile.user 

    if user_profile.activation_key_expiration <= now():
        return JSONResponse({ '__all__': 'Expired activation key. Contact your administrator' }, status=400)

    return JSONResponse({
        'activation_key': user_profile.activation_key,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    })

def activate(request):
    """
    PANDA user activation.
    """
    if request.method == 'POST':
        validator = UserValidation()

        data = dict([(k, v) for k, v in request.POST.items()])

        try:
            user_profile = UserProfile.objects.get(activation_key=data['activation_key'])
        except UserProfile.DoesNotExist:
            return JSONResponse({ '__all__': 'Invalid activation key!' }, status=400)

        user = user_profile.user

        if user_profile.activation_key_expiration <= now():
            return JSONResponse({ '__all__': 'Expired activation key. Contact your administrator.' }, status=400)

        if 'password' not in data:
            return JSONResponse({ 'password': 'This field is required.' }, status=400)

        if 'reenter_password' in data:
            del data['reenter_password']

        bundle = Bundle(data=data)

        errors = validator.is_valid(bundle)

        if errors:
            return JSONResponse(errors, status=400) 

        user.username = bundle.data['email']
        user.email = bundle.data['email']
        user.first_name = bundle.data.get('first_name', '')
        user.last_name = bundle.data.get('last_name', '')
        user.set_password(bundle.data['password'])
        user.is_active = True

        user.save()

        user_profile.activation_key_expiration = now()
        user_profile.save()

        # Success
        return JSONResponse(make_user_login_response(user))
    else:
        # Invalid request
        return JSONResponse(None, status=400)

def forgot_password(request):
    """
    PANDA user password reset and notification.
    """
    if request.method == 'POST':
        try:
            user = UserProxy.objects.get(email=request.POST.get('email'))
        except UserProfile.DoesNotExist:
            return JSONResponse({ '__all__': 'Unknown or inactive email address.' }, status=400)

        if not user.is_active:
            return JSONResponse({ '__all__': 'Unknown or inactive email address.' }, status=400)

        user_profile = user.get_profile()
        user_profile.generate_activation_key()
        user_profile.save()

        email_subject = 'Forgotten password'
        email_body = 'PANDA received a request to change your password.\n\nTo set your new password follow this link:\n\nhttp://%s/#reset-password/%s\n\nIf you did not request this email you should notify your adminstrator.' % (config_value('DOMAIN', 'SITE_DOMAIN'), user_profile.activation_key)

        send_mail(email_subject,
                  email_body,
                  [user.email])

        # Success
        return JSONResponse(make_user_login_response(user))
    else:
        # Invalid request
        return JSONResponse(None, status=400)

def check_available_space(request):
    """
    Check the amount of space left on each disk.
    """
    return JSONResponse({
        'root': {
            'device': os.stat('/').st_dev,
            'free_space': get_free_disk_space('/')
        },
        'uploads': {
            'device':  os.stat(settings.MEDIA_ROOT).st_dev,
            'free_space': get_free_disk_space(settings.MEDIA_ROOT)
        },
        'indices': {
            'device': os.stat(settings.SOLR_DIRECTORY).st_dev,
            'free_space': get_free_disk_space(settings.SOLR_DIRECTORY)
        }
    })

