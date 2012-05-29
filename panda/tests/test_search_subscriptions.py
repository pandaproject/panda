#!/usr/bin/env python

import os.path

from django.conf import settings
from django.test import TransactionTestCase

from panda.models import SearchSubscription
from panda.tasks import RunSubscriptionsTask
from panda.tests import utils

class TestSearchSubscriptions(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        utils.setup_test_solr() 

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)
        self.dataset2 = utils.get_test_dataset(self.user)
        self.upload = utils.get_test_data_upload(self.user, self.dataset)

    def test_subscription_datasets(self):
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

        expected_filename = 'search_subscription_%s.csv' % sub.last_run.isoformat()

        self.assertEqual(os.path.exists(os.path.join(settings.EXPORT_ROOT, expected_filename)), True)

        os.remove(os.path.join(settings.EXPORT_ROOT, expected_filename))

