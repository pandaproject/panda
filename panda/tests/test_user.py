#!/usr/bin/env python

import random
import string

from django.conf import settings
from django.test import TransactionTestCase
from django.utils.timezone import now

from panda import solr
from panda.models import UserProxy
from panda.tests import utils
from tastypie.models import ApiKey

class TestUser(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_panda_user()

    def test_create_user(self):
        new_user = UserProxy.objects.create(
            email="foo@bar.com",
            username="foo@bar.com"
        )

        ApiKey.objects.get(user=new_user)
        new_user.groups.get(name="panda_user")
        user_profile = new_user.get_profile()

        self.assertNotEqual(user_profile, None)
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertGreater(user_profile.activation_key_expiration, now())

    def test_long_email(self):
        long_email = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(100))

        new_user = UserProxy.objects.create(
            email=long_email,
            username=long_email
        )

        ApiKey.objects.get(user=new_user)
        new_user.groups.get(name="panda_user")
        user_profile = new_user.get_profile()

        self.assertNotEqual(user_profile, None)
        self.assertNotEqual(user_profile.activation_key, None)
        self.assertGreater(user_profile.activation_key_expiration, now())

    def test_change_user_reindex(self):
        solr.delete(settings.SOLR_DATASETS_CORE, '*:*') 

        self.user.first_name = 'bazbarfoo'
        self.user.save()

        dataset = utils.get_test_dataset(self.user)
        upload = utils.get_test_data_upload(self.user, dataset)
        
        self.assertEqual(solr.query(settings.SOLR_DATASETS_CORE, dataset.creator.first_name)['response']['numFound'], 1)
        old_name = dataset.creator.first_name

        dataset.creator.first_name = 'foobarbaz'
        dataset.creator.save()

        self.assertEqual(solr.query(settings.SOLR_DATASETS_CORE, old_name)['response']['numFound'], 0)
        self.assertEqual(solr.query(settings.SOLR_DATASETS_CORE, dataset.creator.first_name)['response']['numFound'], 1)

