#!/usr/bin/env python

import logging

from celery.task import Task
from django.conf import settings
from django.utils.timezone import now 

from panda import solr
from panda.utils.notifications import notify

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

            since = sub.last_run.replace(microsecond=0, tzinfo=None)
            since = since.isoformat('T')

            sub.last_run = now()
            sub.save()

            if sub.dataset:
                solr_query = 'dataset_slug:%s AND last_modified:[%s TO *] AND (%s)' % (sub.dataset.slug, since + 'Z', sub.query)
            else:
                solr_query = 'last_modified:[%s TO *] AND (%s)' % (since + 'Z', sub.query)

            response = solr.query(
                settings.SOLR_DATA_CORE,
                solr_query,
                offset=0,
                limit=0
            )

            count = response['response']['numFound'] 

            log.info('Found %i new results' % count)

            if count:
                notify(
                    sub.user,
                    'subscription_results',
                    'info',
                    related_task=None,
                    related_dataset=sub.dataset,
                    related_export=None,
                    extra_context={
                        'query': sub.query,
                        'count': count,
                        'since': since
                    }
                )

        log.info('Finished running subscribed searches')

