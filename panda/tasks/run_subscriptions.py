#!/usr/bin/env python

import logging

from celery.task import Task
from django.conf import settings
from django.utils.timezone import now 

from panda.models import SearchSubscription, TaskStatus
from panda.tasks.export_search import ExportSearchTask

class RunSubscriptionsTask(Task):
    """
    Execute all user-subscribed searches. 
    """
    name = 'panda.tasks.cron.run_subscriptions'

    def run(self, *args, **kwargs):
        log = logging.getLogger(self.name)
        log.info('Running subscribed searches')

        subscriptions = SearchSubscription.objects.all()

        for sub in subscriptions:
            filename = 'search_subscription_%s' % (now().isoformat())

            if sub.dataset:
                description = 'Subscribed search for "%s" in %s.' % (sub.query, sub.dataset.slug)
            else:
                description = 'Subscribed search for %s.' % sub.datasets.slug

            task_type = ExportSearchTask

            task_status = TaskStatus.objects.create(
                task_name=task_type.name,
                task_description=description,
                creator=sub.user
            )

            task_type.apply(
                args=(sub.query, task_status.id),
                kwargs={ 'filename': filename },
                task_id=task_status.id
            )

        log.info('Finished running subscribed searches')

