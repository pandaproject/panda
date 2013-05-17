#!/usr/bin/env python

import logging
import os

from panda.tasks.base import Task
from django.conf import settings
from django.template import Context
from livesettings import config_value

from client.utils import get_total_disk_space, get_free_disk_space
from panda.utils.mail import send_mail
from panda.utils.notifications import get_email_subject_template, get_email_body_template

class RunAdminAlertsTask(Task):
    """
    Notify administrators of anything which requires their attention (disk space, etc).
    """
    name = 'panda.tasks.cron.run_admin_alerts'

    def run(self, *args, **kwargs):
        from panda.models import UserProxy

        log = logging.getLogger(self.name)
        log.info('Running admin alerts')

        # Disk space
        root_disk = os.stat('/').st_dev
        upload_disk = os.stat(settings.MEDIA_ROOT).st_dev
        indices_disk = os.stat(settings.SOLR_DIRECTORY).st_dev

        root_disk_total = get_total_disk_space('/')
        root_disk_free = get_free_disk_space('/')
        root_disk_percent_used = 100 - (float(root_disk_free) / root_disk_total * 100)

        if upload_disk != root_disk:    
            upload_disk_total = get_total_disk_space(settings.MEDIA_ROOT)
            upload_disk_free = get_free_disk_space(settings.MEDIA_ROOT)
            upload_disk_percent_used = 100 - (float(upload_disk_free) / upload_disk_total * 100)
        else:
            upload_disk_total = None
            upload_disk_free = None
            upload_disk_percent_used = None

        if indices_disk != root_disk:
            indices_disk_total = get_total_disk_space(settings.SOLR_DIRECTORY)
            indices_disk_free = get_free_disk_space(settings.SOLR_DIRECTORY)
            indices_disk_percent_used = 100 - (float(indices_disk_free) / indices_disk_total * 100)
        else:
            indices_disk_total = None
            indices_disk_free = None
            indices_disk_percent_used = None

        notify = False

        for free in (root_disk_free, upload_disk_free, indices_disk_free):
            if free is None:
                continue
            
            if free < settings.PANDA_AVAILABLE_SPACE_WARN:
                notify = True

        if notify:
            context = Context({
                'root_disk': root_disk,
                'upload_disk': upload_disk,
                'indices_disk': indices_disk,
                'root_disk_total': root_disk_total,
                'root_disk_free': root_disk_free,
                'root_disk_percent_used': root_disk_percent_used,
                'upload_disk_total': upload_disk_total,
                'upload_disk_free': upload_disk_free,
                'upload_disk_percent_used': upload_disk_percent_used,
                'indices_disk_total': indices_disk_total,
                'indices_disk_free': indices_disk_free,
                'indices_disk_percent_used': indices_disk_percent_used,
                'settings': settings,
                'site_domain': config_value('DOMAIN', 'SITE_DOMAIN')
            })

            # Don't HTML escape plain-text emails
            context.autoescape = False

            email_subject = get_email_subject_template('disk_space_alert').render(context)
            email_message = get_email_body_template('disk_space_alert').render(context)

            recipients = UserProxy.objects.filter(is_superuser=True, is_active=True)

            send_mail(email_subject.strip(), email_message, [r.email for r in recipients])

        log.info('Finished running admin alerts')

