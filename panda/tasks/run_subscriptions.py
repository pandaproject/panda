#!/usr/bin/env python

import logging

from panda.tasks.base import Task
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
   
            solr_query = 'last_modified:[%s TO *] AND (%s)' % (since + 'Z', sub.query)

            if sub.dataset:
                solr_query += ' dataset_slug:%s' % (sub.dataset.slug)
            elif sub.category:
                dataset_slugs = sub.category.datasets.values_list('slug', flat=True)
                solr_query += ' dataset_slug:(%s)' % ' '.join(dataset_slugs)

            response = solr.query(
                settings.SOLR_DATA_CORE,
                solr_query,
                offset=0,
                limit=0
            )

            count = response['response']['numFound'] 

            log.info('Found %i new results' % count)

            if count:
                if sub.dataset:
                    url = '#dataset/%s/search/%s/%s' % (sub.dataset.slug, sub.query_url, since)
                elif sub.category:
                    url = '#search/%s/%s/%s' % (sub.category.slug, sub.query, since)
                else:
                    url = '#search/all/%s/%s' % (sub.query, since)
                    
                notify(
                    sub.user,
                    'subscription_results',
                    'info',
                    url=url,
                    extra_context={
                        'query': sub.query,
                        'query_url': sub.query_url,
                        'category': sub.category,
                        'related_dataset': sub.dataset,
                        'count': count,
                        'since': since
                    }
                )

        log.info('Finished running subscribed searches')

