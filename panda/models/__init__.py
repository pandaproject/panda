#!/usr/bin/env python

import random
import sha

from django.contrib.auth.models import Group, User
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from livesettings import config_value
from tastypie.models import ApiKey

from panda import config # Needed for autodiscovery
from panda.models.activity_log import ActivityLog
from panda.models.category import Category
from panda.models.dataset import Dataset
from panda.models.data_upload import DataUpload
from panda.models.export import Export
from panda.models.notification import Notification 
from panda.models.related_upload import RelatedUpload
from panda.models.search_log import SearchLog
from panda.models.task_status import TaskStatus
from panda.models.user_profile import UserProfile
from panda.utils.mail import send_mail

__all__ = ['ActivityLog', 'Category', 'Dataset', 'DataUpload', 'Export', 'Notification', 'RelatedUpload', 'SearchLog', 'TaskStatus', 'UserProfile']

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
            activation_key=activation_key,
            activation_key_expiration=now() + settings.PANDA_ACTIVATION_PERIOD 
        )

        email_subject = 'Welcome to PANDA, please activate your account!'
        email_body = 'Hello there, the administrator of your organization\'s PANDA has signed you up for an account.\n\nTo activate your account, click this link:\n\nhttp://%s/#activate/%s' % (config_value('DOMAIN', 'SITE_DOMAIN'), user_profile.activation_key)

        send_mail(email_subject,
                  email_body,
                  [instance.email])

