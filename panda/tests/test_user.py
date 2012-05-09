#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase
from django.utils.timezone import now

from django.contrib.auth.models import User
from panda.tests import utils
from tastypie.models import ApiKey

class TestUser(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_panda_user()

    def test_create_user(self):
        new_user = User.objects.create(
            email="foo@bar.com",
            username="foo@bar.com"
        )

        ApiKey.objects.get(user=new_user)
        new_user.groups.get(name="panda_user")
        user_profile = new_user.get_profile()

        self.assertNotEqual(user_profile, None)
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertGreater(user_profile.activation_key_expiration, now())

