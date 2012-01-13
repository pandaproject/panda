#!/usr/bin/env python

import random
import sha

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from livesettings import config_value
from tastypie.models import ApiKey

from redd import config # Needed for autodiscovery
from redd import solr
from redd.models.category import Category
from redd.models.dataset import Dataset
from redd.models.data_upload import DataUpload
from redd.models.notification import Notification 
from redd.models.related_upload import RelatedUpload
from redd.models.task_status import TaskStatus
from redd.models.user_profile import UserProfile
from redd.utils.mail import send_mail

__all__ = ['Category', 'Dataset', 'DataUpload', 'Notification', 'RelatedUpload', 'TaskStatus', 'UserProfile']

@receiver(models.signals.post_save, sender=User)
def on_user_post_save(sender, instance, created, **kwargs):
    """
    When a User is created, create an API key for them,
    add them to the panda_user group and send them an activation email.
    When a User is saved, update their Datasets' metadata in Solr. 
    """
    # Setup activation
    if created and not kwargs.get('raw', False):
        ApiKey.objects.get_or_create(user=instance)

        panda_users = Group.objects.get(name='panda_user')
        instance.groups.add(panda_users)

        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt + instance.username).hexdigest()

        user_profile = UserProfile.objects.create(
            user=instance,
            activation_key=activation_key
        )

        email_subject = 'Welcome to PANDA, please activate your account!'
        email_body = 'Hello there, the administrator of your organization\'s PANDA has signed you up for an account.\n\nTo activate your account, click this link:\n\nhttp://%s/#activate/%s' % (config_value('DOMAIN', 'SITE_DOMAIN'), user_profile.activation_key)

        send_mail(email_subject,
                  email_body,
                  [instance.email])
    # Update full text
    else:
        has_datasets = False

        # TODO - shouldn't really do this for a password change...
        for dataset in instance.datasets.all():
            has_datasets = True
            dataset.update_full_text(commit=False)

        if has_datasets:
            solr.commit(settings.SOLR_DATASETS_CORE)

