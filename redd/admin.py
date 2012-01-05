#!/usr/bin/env python

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _
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

class PandaUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)

    username = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that email address already exists."))

    def save(self, commit=True):
        user = super(PandaUserCreationForm, self).save(commit=False)
        # TODO
        #user.set_password(self.cleaned_data["password1"])
        # TODO - generate API key
        # TODO - add to panda_user group
        if commit:
            user.save()
        return user

# Add API key reference to User admin
class UserModelAdmin(UserAdmin):
    inlines = [ApiKeyInline]
    add_form = PandaUserCreationForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',)}
        ),
    )

    def add_view(self, request, form_url='', extra_context=None):
        return super(UserModelAdmin, self).add_view(request, form_url, extra_context)

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserModelAdmin)

admin.site.register(Category)
admin.site.register(TaskStatus)

