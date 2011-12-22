#!/usr/bin/env python

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask, TaskState, WorkerState
from tastypie.admin import ApiKeyInline
from tastypie.models import ApiKey

from redd.models import Category, TaskStatus 

# Hide celery monitors
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)

# Register tastypie models
admin.site.register(ApiKey)

# Add API key reference to User admin
class UserModelAdmin(UserAdmin):
    inlines = [ApiKeyInline]

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserModelAdmin)

admin.site.register(Category)
admin.site.register(TaskStatus)

