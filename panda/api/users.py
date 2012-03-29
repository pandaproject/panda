#!/usr/bin/env python

import random

from django.contrib.auth.models import Group, User, get_hexdigest
from django.core.validators import email_re
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.validation import Validation

from panda.api.utils import PandaApiKeyAuthentication, PandaSerializer, PandaModelResource

class UserValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'email' not in bundle.data or not bundle.data['email']:
            errors['email'] = ['This field is required.']
        elif not email_re.match(bundle.data['email']):
            errors['email'] = ['Email address is not valid.']

        return errors

class UserResource(PandaModelResource):
    """
    API resource for Uploads.
    """
    # Write-only! See dehydrate().
    password = fields.CharField(attribute='password')

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['username', 'is_staff', 'is_superuser']
        always_return_data = True

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        validation = UserValidation()
        serializer = PandaSerializer()

    def hydrate_email(self, bundle):
        """
        Copy the email to the username field.
        """
        bundle.data['email'] = bundle.data['email'].lower()
        bundle.data['username'] = bundle.data['email'].lower()

        return bundle

    def hydrate_password(self, bundle):
        """
        Encode new passwords.
        """
        if 'password' in bundle.data and bundle.data['password']:
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, bundle.data['password'])

            bundle.data['password'] = '%s$%s$%s' % (algo, salt, hsh)
        else:
            # A blank password marks the user as unable to login
            bundle.data['password'] = '' 

        return bundle

    def dehydrate(self, bundle):
        """
        Always remove the password form the serialized bundle.
        """
        del bundle.data['password']

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Create user using email as username and optionally using a supplied password.

        All users created via the API are automatically assigned to the panda_users group.
        """
        bundle = super(UserResource, self).obj_create(bundle, request=request, username=bundle.data['email'], password=bundle.data.get('password', ''), **kwargs)

        panda_user = Group.objects.get(name='panda_user')

        bundle.obj.groups.add(panda_user)
        bundle.obj.save()

        return bundle

