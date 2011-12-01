#!/usr/bin/env python

import random

from django.contrib.auth.models import Group, User, get_hexdigest
from django.core.validators import email_re
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.validation import Validation

from redd.api.utils import CustomApiKeyAuthentication, CustomSerializer

class UserValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'email' in bundle.data and bundle.data['email']:
            if not email_re.match(bundle.data['email']):
                errors['email'] = ['Email address is not valid.']

            bundle.data['email'] = bundle.data['email'].lower()
            bundle.data['username'] = bundle.data['email'].lower()
        else:
            errors['email'] = ['This field is required.']

        if 'password' in bundle.data and bundle.data['password']:
            # Password hashing algorithm taken from Django
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, bundle.data['password'])

            bundle.data['password'] = '%s$%s$%s' % (algo, salt, hsh)
        else:
            bundle.data['password'] = None

        return errors

class UserResource(ModelResource):
    """
    API resource for Uploads.
    """
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['password', 'username', 'is_superuser', 'is_staff']
        always_return_data = True

        authentication = CustomApiKeyAuthentication()
        authorization = DjangoAuthorization()
        validation = UserValidation()
        serializer = CustomSerializer()

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Create user using email as username and optionally using a supplied password.

        All users created via the API are automatically assigned to the panda_users group.
        """
        bundle = super(UserResource, self).obj_create(bundle, request=request, username=bundle.data['username'], password=bundle.data['password'], **kwargs)

        panda_user = Group.objects.get(name='panda_user')

        bundle.obj.groups.add(panda_user)
        bundle.obj.save()

        return bundle

