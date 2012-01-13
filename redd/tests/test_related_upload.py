#!/usr/bin/env python

import os.path
from shutil import copyfile

from django.conf import settings
from django.test import TransactionTestCase

from redd.models import RelatedUpload 
from redd.tests import utils

class TestRelatedUpload(TransactionTestCase):
    fixtures = ['init_panda.json']

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = utils.get_panda_user()
        self.dataset = utils.get_test_dataset(self.user)

        try:
            os.mkdir(settings.MEDIA_ROOT)
        except OSError:
            pass

        src = os.path.join(utils.TEST_DATA_PATH, utils.TEST_DATA_FILENAME)
        dst = os.path.join(settings.MEDIA_ROOT, utils.TEST_DATA_FILENAME)
        copyfile(src, dst)

        self.upload = RelatedUpload.objects.create(
            filename=utils.TEST_DATA_FILENAME,
            original_filename=utils.TEST_DATA_FILENAME,
            size=os.path.getsize(dst),
            creator=self.user,
            dataset=self.dataset)

    def test_created(self):
        self.assertEqual(self.upload.original_filename, utils.TEST_DATA_FILENAME)
        self.assertEqual(self.upload.creator, self.user)
        self.assertNotEqual(self.upload.creation_date, None)
        self.assertEqual(self.upload.dataset, self.dataset)

