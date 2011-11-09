#!/usr/bin/env python

from django.contrib.auth.models import User, get_hexdigest
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.validation import Validation

from redd.api.utils import CustomApiKeyAuthentication

class UserValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return { '__all__': 'No user data submitted.' }

        errors = {}

        if 'username' in bundle.data:
            # TODO - verify only letters and numbers
            pass
        else:
            errors['username'] = ['This field is required.']

        if 'email' in bundle.data:
            # TODO - verify email format
            pass
        else:
            errors['email'] = ['This field is required.']

        if 'password' in bundle.data:
            import random

            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, bundle.data['password'])

            bundle.data['password'] = '%s$%s$%s' % (algo, salt, hsh)

        return errors

class UserResource(ModelResource):
    """
    API resource for Uploads.
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['password', 'username']

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        validation = UserValidation()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(UserResource, self).obj_create(bundle, request=request, username=bundle.data['username'], **kwargs)

    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.username 

        return bundle

