#!/usr/bin/env python

import logging
from urllib import unquote

from celery.task import Task
from django.conf import settings
from django.utils.timezone import now 
from livesettings import config_value

from panda import solr
from panda.utils.mail import send_mail

class RunSubscriptionsTask(Task):
    """
    Execute all user-subscribed searches. 
    """
    name = 'panda.tasks.cron.run_subscriptions'

    def run(self, *args, **kwargs):
        from panda.models import SearchSubscription

        log = logging.getLogger(self.name)
        log.info('Running subscribed searches')

        subscriptions = SearchSubscription.objects.all()

        for sub in subscriptions:
            log.info('Running subscription: %s' % sub)

            sub.last_run = now()
            sub.save()

            if sub.dataset:
                solr_query = 'dataset_slug:%s %s' % (sub.dataset.slug, sub.query)
                response = solr.query(
                    settings.SOLR_DATA_CORE,
                    solr_query,
                    offset=0,
                    limit=0
                )

                count = response['response']['numFound'] 
            else:
                # TODO
                pass

            self.send_notification(sub, count)

        log.info('Finished running subscribed searches')

    def send_notification(self, sub, count):
        """
        Send a user a notification of new results.
        """
        from panda.models import Notification

        dataset_name = unquote(sub.dataset.name)

        email_subject = 'New search results for "%s" in %s' % sub.query, dataset_name
        # TODO: links
        email_message = 'See just the new results:\n\nhttp://%s/#dataset/%s/%s\n\nSee all results for your search:\n\nhttp://%s/#dataset/%s/%s' % (config_value('DOMAIN', 'SITE_DOMAIN'), sub.dataset.slug, sub.query, config_value('DOMAIN', 'SITE_DOMAIN'), sub.dataset.slug, sub.query)
        notification_message = 'New search results for: <strong>%s</strong>' % sub.query

        notification_type = 'Info'

        Notification.objects.create(
            recipient=sub.user,
            related_task=None,
            related_dataset=sub.dataset,
            related_export=None,
            message=notification_message,
            type=notification_type
        )
        
        send_mail(email_subject, email_message, [sub.user.username])

