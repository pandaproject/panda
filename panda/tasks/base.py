from celery.task import Task as CeleryTask
from celery.contrib.abortable import AbortableTask as CeleryAbortableTask
from django.utils import translation
from django.conf import settings
import logging
log = logging.getLogger('panda.tasks.base')

class Task(CeleryTask):
    def __init__(self,*args,**kwargs):
        if settings.USE_I18N:
            try:
                translation.activate(settings.LANGUAGE_CODE)
            except Exception, e:
                log.warn("Error activating translation library", e)
        super(CeleryTask,self).__init__(*args,**kwargs)

class AbortableTask(CeleryAbortableTask):
    def __init__(self,*args,**kwargs):
        if settings.USE_I18N:
            try:
                translation.activate(settings.LANGUAGE_CODE)
            except Exception, e:
                log.warn("Error activating translation library", e)
        super(CeleryAbortableTask,self).__init__(*args,**kwargs)

