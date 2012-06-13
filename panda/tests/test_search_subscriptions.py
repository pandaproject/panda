#!/usr/bin/env python

from django.conf import settings
from django.test import TransactionTestCase

from panda.models import Notification, SearchSubscription
from panda.tasks import RunSubscriptionsTask
from panda.tests import utils

class TestSearchSubscriptions(TransactionTestCase):
    fixtures = ['init_panda.json', 'test_users.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.dataset2 = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_subscription_dataset(self):
        self.dataset.import_data(self.user, self.upload)

        sub = SearchSubscription.objects.create(
            user=self.user,
            dataset=self.dataset,
            query='*'
        )

        last_run = sub.last_run

        RunSubscriptionsTask.apply_async()

        # Refresh from database
        sub = SearchSubscription.objects.get(pk=sub.pk)

        self.assertNotEqual(last_run, sub.last_run)

        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 2)

    def test_subscription_global(self):
        self.dataset.import_data(self.user, self.upload)

        sub = SearchSubscription.objects.create(
            user=self.user,
            dataset=None,
            query='*'
        )

        last_run = sub.last_run

        RunSubscriptionsTask.apply_async()

        # Refresh from database
        sub = SearchSubscription.objects.get(pk=sub.pk)

        self.assertNotEqual(last_run, sub.last_run)

        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 2)

