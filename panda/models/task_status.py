#!/usr/bin/env python

from celery import states
from celery.contrib.abortable import AbortableAsyncResult
from django.db import models
from django.utils.timezone import now 
from djcelery.models import TASK_STATE_CHOICES

from panda.models.user_proxy import UserProxy

TASK_STATUS_CHOICES = TASK_STATE_CHOICES
TASK_STATUS_CHOICES.extend([
    ('ABORTED', 'ABORTED'),
    ('ABORT REQUESTED', 'ABORT REQUESTED')
])

class TaskStatus(models.Model):
    """
    An object to track the status of a Celery task, as the
    data available in AsyncResult is not sufficient.
    """
    task_name = models.CharField(max_length=255,
        help_text='Identifying name for this task.')
    task_description = models.TextField(
        help_text='Description of the task.')
    status = models.CharField(max_length=50, default=states.PENDING, choices=TASK_STATUS_CHOICES,
        help_text='Current state of this task.')
    message = models.CharField(max_length=255, blank=True,
        help_text='A human-readable message indicating the progress of this task.')
    start = models.DateTimeField(null=True,
        help_text='Date and time that this task began processing.')
    end = models.DateTimeField(null=True,
        help_text='Date and time that this task ceased processing (either complete or failed).')
    traceback = models.TextField(blank=True, null=True, default=None,
        help_text='Traceback that exited this task, if it failed.')
    creator = models.ForeignKey(UserProxy, null=True, related_name='tasks',
        help_text='The user who initiated this task.')

    class Meta:
        app_label = 'panda'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __unicode__(self):
        return self.task_description or self.task_name

    def request_abort(self):
        """
        Set flag to abort this task if it is still running.
        """
        if not self.end:
            async_result = AbortableAsyncResult(self.id)
            async_result.abort()

            self.status = 'ABORT REQUESTED'
            self.save()

    def begin(self, message):
        """
        Mark that task has begun.
        """
        self.status = 'STARTED' 
        self.start = now()
        self.message = message 
        self.save()

    def update(self, message):
        """
        Update task status message.
        """
        self.message = message 
        self.save()

    def abort(self, message):
        """
        Mark that task has aborted.
        """
        self.status = 'ABORTED'
        self.end = now()
        self.message = message
        self.save()

    def complete(self, message):
        """
        Mark that task has completed.
        """
        self.status = 'SUCCESS'
        self.end = now()
        self.message = message
        self.save()

    def exception(self, message, formatted_traceback):
        """
        Mark that task raised an exception
        """
        self.status = 'FAILURE'
        self.end = now()
        self.message = message 
        self.traceback = formatted_traceback
        self.save()

