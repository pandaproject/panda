#!/usr/bin/env python

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

from redd.models import Category, Dataset, Notification, TaskStatus, Upload 

# Register tastypie models
admin.site.register(ApiKey)
admin.site.register(ApiAccess)

# Add API key reference to User admin
class UserModelAdmin(UserAdmin):
    inlines = [ApiKeyInline]

admin.site.unregister(User)
admin.site.register(User, UserModelAdmin)

# Custom Redd admins
class DatasetAdmin(admin.ModelAdmin):
    readonly_fields = ('schema', 'sample_data', 'dialect')

admin.site.register(Category)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Notification)
admin.site.register(TaskStatus)
admin.site.register(Upload)



