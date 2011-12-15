#!/usr/bin/env python

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from tastypie.models import ApiKey

from redd import solr
from redd.models.category import Category
from redd.models.dataset import Dataset
from redd.models.notification import Notification 
from redd.models.task_status import TaskStatus
from redd.models.upload import Upload

__all__ = ['Category', 'Dataset', 'Notification', 'TaskStatus', 'Upload']

@receiver(models.signals.post_save, sender=User)
def create_api_key(sender, **kwargs):
    """
    A signal for hooking up automatic ``ApiKey`` creation.
    """
    if kwargs.get('created') is True:
        ApiKey.objects.get_or_create(user=kwargs.get('instance'))

@receiver(models.signals.post_save, sender=User)
def on_user_save(sender, **kwargs):
    """
    When a User is saved, update their Datasets' metadata in Solr. 
    """
    if kwargs.get('created') is True:
        return
        
    for dataset in kwargs['instance'].datasets.all():
        dataset.update_full_text(commit=False)

    solr.commit(settings.SOLR_DATASETS_CORE)

