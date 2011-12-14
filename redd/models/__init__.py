#!/usr/bin/env python

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from tastypie.models import ApiKey

from redd.models.category import Category
from redd.models.dataset import Dataset
from redd.models.notification import Notification 
from redd.models.task_status import TaskStatus
from redd.models.upload import Upload

@receiver(models.signals.post_save, sender=User)
def create_api_key(sender, **kwargs):
    """
    A signal for hooking up automatic ``ApiKey`` creation.
    """
    if kwargs.get('created') is True:
        ApiKey.objects.get_or_create(user=kwargs.get('instance'))

