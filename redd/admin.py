#!/usr/bin/env python

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

from redd.models import Category, Dataset, Notification, TaskStatus, Upload 

admin.site.register(ApiKey)
admin.site.register(ApiAccess)

admin.site.register(Category)
admin.site.register(Dataset)
admin.site.register(Notification)
admin.site.register(TaskStatus)
admin.site.register(Upload)

class UserModelAdmin(UserAdmin):
    inlines = [ApiKeyInline]

admin.site.unregister(User)
admin.site.register(User, UserModelAdmin)

