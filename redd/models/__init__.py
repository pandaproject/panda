#!/usr/bin/env python

import random
import sha

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
from redd.models.user_profile import UserProfile
from redd.utils.email import panda_email

__all__ = ['Category', 'Dataset', 'Notification', 'TaskStatus', 'Upload', 'UserProfile']

@receiver(models.signals.post_save, sender=User)
def on_user_post_save(sender, instance, created, **kwargs):
    """
    When a User is created, create an API key and send them an activation email.
    When a User is saved, update their Datasets' metadata in Solr. 
    """
    # Setup activation
    if created and not kwargs.get('raw', False):
        ApiKey.objects.get_or_create(user=instance)

        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt + instance.username).hexdigest()

        user_profile = UserProfile.objects.create(
            user=instance,
            activation_key=activation_key
        )

        email_subject = 'Welcome to PANDA, please activate your account!'
        email_body = 'Hello there, the administrator of your organization\'s PANDA has signed you up for an account.\n\nTo activate your account, click this link:\n\nhttp://%s/#activate/%s' % (settings.SITE_DOMAIN, user_profile.activation_key)

        panda_email(email_subject,
                  email_body,
                  [instance.email])
    # Update full text
    else:
        # TODO - shouldn't really do this for a password change...
        for dataset in instance.datasets.all():
            dataset.update_full_text(commit=False)

        solr.commit(settings.SOLR_DATASETS_CORE)

