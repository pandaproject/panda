#!/user/bin/env python

import random
import sha

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from livesettings import config_value

from panda.models.user_proxy import UserProxy
from panda.utils.mail import send_mail

class UserProfile(models.Model):
    """
    User metadata such as their activation key.
    """
    user = models.OneToOneField(UserProxy,
        verbose_name=_('user'))

    activation_key = models.CharField(_('activation_key'), max_length=40, null=True, blank=True)
    activation_key_expiration = models.DateTimeField(_('activation_key_expiration'))

    # NB: This field is no longer used.
    show_login_help = models.BooleanField(_('show_login_help'), default=True, help_text='This field is no longer used.')

    class Meta:
        app_label = 'panda'
        verbose_name = _('UserProfile')
        verbose_name_plural = _('UserProfiles')

    def generate_activation_key(self):
        salt = sha.new(str(random.random())).hexdigest()[:5]
        self.activation_key = sha.new(salt + self.user.username).hexdigest()
        self.activation_key_expiration=now() + settings.PANDA_ACTIVATION_PERIOD

    def send_activation_email(self):
        email_subject = _('Welcome to PANDA, please activate your account!')
        email_body = _('Hello there, the administrator of your organization\'s PANDA has signed you up for an account.\n\nTo activate your account, click this link:\n\nhttp://%(site_domain)s/#activate/%(activation_key)s') \
             % {'site_domain': config_value('DOMAIN', 'SITE_DOMAIN'), 'activation_key': self.activation_key}

        send_mail(email_subject,
                  email_body,
                  [self.user.email])

