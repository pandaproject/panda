#!/user/bin/env python

import random
import sha

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from livesettings import config_value

from panda.utils.mail import send_mail

class UserProfile(models.Model):
    """
    User metadata such as their activation key.
    """
    user = models.OneToOneField(User)

    activation_key = models.CharField(max_length=40, null=True, blank=True)
    activation_key_expiration = models.DateTimeField()

    class Meta:
        app_label = 'panda'

    def generate_activation_key(self):
        salt = sha.new(str(random.random())).hexdigest()[:5]
        self.activation_key = sha.new(salt + self.user.username).hexdigest()
        self.activation_key_expiration=now() + settings.PANDA_ACTIVATION_PERIOD

    def send_activation_email(self):
        email_subject = 'Welcome to PANDA, please activate your account!'
        email_body = 'Hello there, the administrator of your organization\'s PANDA has signed you up for an account.\n\nTo activate your account, click this link:\n\nhttp://%s/#activate/%s' % (config_value('DOMAIN', 'SITE_DOMAIN'), self.activation_key)

        send_mail(email_subject,
                  email_body,
                  [self.user.email])

