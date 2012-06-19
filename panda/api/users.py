#!/usr/bin/env python

from django.conf.urls.defaults import url
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import email_re
from tastypie import fields
from tastypie import http
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie.resources import NOT_AVAILABLE
from tastypie.utils.urls import trailing_slash
from tastypie.validation import Validation

from panda.api.utils import PandaApiKeyAuthentication, PandaSerializer, PandaModelResource
from panda.models import UserProxy

class UserValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if 'email' not in bundle.data or not bundle.data['email']:
            errors['email'] = ['This field is required.']
        elif not email_re.match(bundle.data['email']):
            errors['email'] = ['Email address is not valid.']

        return errors

class UserAuthorization(Authorization):
    def is_authorized(self, request, obj=None):
        """
        Superusers can change any other user. Regular users can only GET and
        PUT to their own user.
        """
        if request.method in ['GET', 'PUT']:
            return True
        else:
            return request.user.is_superuser

class UserResource(PandaModelResource):
    """
    API resource for Uploads.
    """
    # Write-only! See dehydrate().
    password = fields.CharField(attribute='password')

    class Meta:
        queryset = UserProxy.objects.all()
        resource_name = 'user'
        allowed_methods = ['get', 'post', 'put', 'delete']
        excludes = ['username', 'is_staff', 'is_superuser']
        always_return_data = True

        authentication = PandaApiKeyAuthentication()
        authorization = UserAuthorization()
        validation = UserValidation()
        serializer = PandaSerializer()

    def override_urls(self):
        """
        Add urls for search endpoint.
        """
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/login_help%s$' % (self._meta.resource_name, trailing_slash()), self.wrap_view('login_help'), name='api_user_login_help'),
        ]

    def hydrate_email(self, bundle):
        """
        Copy the email to the username field.
        """
        if 'email' in bundle.data:
            bundle.data['email'] = bundle.data['email'].lower()

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
        if not request.user.is_superuser:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        bundle = super(UserResource, self).obj_create(bundle, request=request, username=bundle.data['email'], **kwargs)
        bundle.obj.set_password(bundle.data.get('password'))

        panda_user = Group.objects.get(name='panda_user')

        bundle.obj.groups.add(panda_user)
        bundle.obj.save()

        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not bundle.obj.pk:
            # Attempt to hydrate data from kwargs before doing a lookup for the object.
            # This step is needed so certain values (like datetime) will pass model validation.
            try:
                bundle.obj = self.get_object_list(bundle.request).model()
                bundle.data.update(kwargs)
                bundle = self.full_hydrate(bundle)
                lookup_kwargs = kwargs.copy()

                for key in kwargs.keys():
                    if key == 'pk':
                        continue
                    elif getattr(bundle.obj, key, NOT_AVAILABLE) is not NOT_AVAILABLE:
                        lookup_kwargs[key] = getattr(bundle.obj, key)
                    else:
                        del lookup_kwargs[key]
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle.request, **lookup_kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        # CHECK AUTHORIZATION 
        if request and not request.user.is_superuser and bundle.obj.id != request.user.id:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if bundle.errors and not skip_errors:
            self.error_response(bundle.errors, request)

        # SET USERNAME FROM EMAIL
        bundle.obj.username = bundle.obj.email

        # SET PASSWORD
        if 'password' in bundle.data:
            bundle.obj.set_password(bundle.data.get('password'))

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)

        return bundle

    def login_help(self, request, **kwargs):
        """
        Set the status of the "show_login_help" flag.
        """
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if 'pk' in kwargs:
            get_id = int(kwargs['pk'])
        else:
            get_id = int(request.GET.get('id', ''))

        # CHECK AUTHORIZATION 
        if request and not request.user.is_superuser and get_id != request.user.id:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)

        if not 'show_login_help' in deserialized:
            raise BadRequest("Invalid data sent.")

        user = UserProxy.objects.get(id=get_id)
        profile = user.get_profile()

        profile.show_login_help = deserialized['show_login_help']
        profile.save()

        return self.create_response(request, {}, response_class=http.HttpAccepted) 

