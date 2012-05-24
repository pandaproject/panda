#!/usr/bin/env python

from django.contrib.auth.models import User
from django.conf import settings

from panda import solr

class UserProxy(User):
    """
    User Django's ProxyModel concept to track changes to the User
    model without overriding it. This way related datasets can be
    updated when user details change. Inspired by:

    http://stackoverflow.com/questions/1817244/override-default-user-model-method
    http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
    """
    __original_first_name = None
    __original_last_name = None
    __original_email = None

    class Meta:
        proxy = True
        app_label = 'panda'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_first_name = self.first_name
        self.__original_last_name = self.last_name
        self.__original_email = self.email

    def save(self, *args, **kwargs):
        if self.first_name != self.__original_first_name or \
            self.last_name != self.__original_last_name or \
            self.email != self.__original_email:

            if self.datasets.count():
                for dataset in self.datasets.all():
                    dataset.update_full_text(commit=False)
                
                solr.commit(settings.SOLR_DATASETS_CORE)

        super(User, self).save(*args, **kwargs)

        self.__original_first_name = self.first_name
        self.__original_last_name = self.last_name
        self.__original_email = self.email

