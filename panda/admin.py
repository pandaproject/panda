#!/usr/bin/env python

from StringIO import StringIO

from django import forms
from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask, TaskState, WorkerState
from livesettings import config_value
from tastypie.admin import ApiKeyInline
from tastypie.models import ApiKey

from csvkit import CSVKitReader
from csvkit.sniffer import sniff_dialect as csvkit_sniff
from panda import solr
from panda.models import Category, TaskStatus, UserProfile, UserProxy

# Hide celery monitors
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)

class PandaUserCreationForm(forms.ModelForm):
    """
    Custom User creation form that eliminates duplication between username
    and email.
    """
    class Meta:
        model = UserProxy
        fields = ("email",)

    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        email = self.cleaned_data["email"]
        
        try:
            UserProxy.objects.get(email=email)
        except UserProxy.DoesNotExist:
            return email

        raise forms.ValidationError(_("A user with that email address already exists."))

    def save(self, commit=True):
        user = super(PandaUserCreationForm, self).save(commit=False)
        user.email = user.email.lower()
        user.username = user.email
        user.is_active = False

        if commit:
            user.save()

        return user

class PandaUserChangeForm(UserChangeForm):
    """
    Customized User change form that allows password to be blank.
    (for editing unactivated accounts)
    """
    class Media:
        js = ('panda_user_change_form.js',)

    def __init__(self, *args, **kwargs):
        super(PandaUserChangeForm, self).__init__(*args, **kwargs)

        # We edit the email field and copy it to the username field
        del self.fields['username']
        
        self.fields['password'].required = False

    def save(self, commit=True):
        user = super(PandaUserChangeForm, self).save(commit=False)
        user.email = user.email.lower()
        user.username = user.email

        if commit:
            user.save()

        return user

class PandaApiKeyInline(ApiKeyInline):
    """
    Customized ApiKeyInline that doesn't allow the creation date to be modified.
    """
    readonly_fields = ('created',)

class UserProfileInline(admin.StackedInline):
    """
    Inline for UserProfile which does not allow the activation key to be modified. 
    """
    model = UserProfile
    
    readonly_fields = ('activation_key', 'activation_key_expiration')

class UserModelAdmin(UserAdmin):
    """
    Heavily modified admin page for editing Users. Eliminates duplication between
    username and email fields. Hides unnecessary cruft. Makes timestamp fields
    readonly. Etc.
    """
    inlines = [UserProfileInline, PandaApiKeyInline]
    add_form = PandaUserCreationForm
    form = PandaUserChangeForm

    add_form_template = 'admin/panda/userproxy/add_form.html'

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name')}
        ),
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)

    readonly_fields = ('last_login', 'date_joined')

    actions = ['resend_activation']

    def get_urls(self):
        urls = super(UserModelAdmin, self).get_urls()
        custom_urls = patterns('',
            url(r'^(.+)/resend_activation$',
                self.admin_site.admin_view(self.resend_activation_single),
                name='%s_%s_resend_activation' % (self.model._meta.app_label, self.model._meta.module_name)
            ),
            url(r'^add_many/$',
                self.admin_site.admin_view(self.add_many),
                name='%s_%s_add_many' % (self.model._meta.app_label, self.model._meta.module_name)
            ),
        )

        return custom_urls + urls

    def resend_activation_single(self, request, pk):
        if not config_value('EMAIL', 'EMAIL_ENABLED'):
            self.message_user(request, 'Email is not configured for your PANDA.')

            return HttpResponseRedirect(
                reverse('admin:panda_userproxy_change', args=[pk])
            )

        user = get_object_or_404(UserProxy, pk=pk)
        user_profile = user.get_profile()

        user_profile.generate_activation_key()
        user_profile.save()

        user_profile.send_activation_email()
        self.message_user(request, 'Activation email sent.')

        return HttpResponseRedirect(
            reverse('admin:panda_userproxy_change', args=[pk])
        )

    def resend_activation(self, request, queryset):
        if not config_value('EMAIL', 'EMAIL_ENABLED'):
            self.message_user(request, 'Email is not configured for your PANDA.')
            return HttpResponseRedirect(
                reverse('admin:panda_userproxy_changelist')
            )

        users = list(queryset)

        for user in users:
            user_profile = user.get_profile()

            user_profile.generate_activation_key()
            user_profile.save()

            user_profile.send_activation_email()

        self.message_user(request, 'Sent %i activation emails.' % len(users))

    resend_activation.short_description = 'Resend activation email(s)'

    @transaction.commit_on_success
    def add_many(self, request, extra_context=None):
        model = self.model
        opts = model._meta

        context = RequestContext(request, {
            'opts': opts,
            'title': _('Add %s') % force_unicode(opts.verbose_name_plural),
            'media': self.media,
            'error': [],
            'app_label': opts.app_label,
            'email_enabled': config_value('EMAIL', 'EMAIL_ENABLED')
        })
        
        context.update(extra_context or {})

        if request.method == 'POST':
            try:
                user_data = request.POST.get('user-data', '') 

                if not user_data:
                    raise Exception('No user data provided.')

                context['user_data'] = user_data

                try:
                    csv_dialect = csvkit_sniff(user_data)
                except UnicodeDecodeError:
                    raise Exception('Only UTF-8 data is supported.')

                if not csv_dialect:
                    raise Exception('Unable to determine the format of the data you entered. Please ensure it is valid CSV data.')

                reader = CSVKitReader(StringIO(user_data), dialect=csv_dialect)

                emails = 0

                for i, row in enumerate(reader):
                    if len(row) < 4:
                        raise Exception('Row %i has less than 4 columns.' % i)
                    if len(row) > 4:
                        raise Exception('Row %i has more than 4 columns.' % i)

                    if UserProxy.objects.filter(email=row[0]).count():
                        raise Exception('User "%s" already exists'  % row[0])

                    user = UserProxy.objects.create_user(row[0], row[0], row[1] or None)
                    user.is_active = bool(row[1]) # active if a password is provided
                    user.first_name = row[2]
                    user.last_name = row[3]
                    user.save()

                    ApiKey.objects.get_or_create(user=user)

                    if not row[1] and config_value('EMAIL', 'EMAIL_ENABLED'):
                        emails += 1

                self.message_user(request, 'Successfully created %i user(s)' % (i + 1))

                if emails:
                    self.message_user(request, 'Sent %i activation email(s)' % emails)
            except Exception, e:
                context['error'] = e.message

        return render_to_response('admin/panda/userproxy/add_many_form.html', context)

    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        """
        This method is overriden in its entirety so that the ApiKey inline won't be
        displayed/parsed on the add_form page.
        """
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                form_validated = False
                new_object = self.model()
            
            PANDA_SKIP_INLINES="""prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix, queryset=inline.queryset(request))
                formsets.append(formset)
            if all_valid(formsets) and form_validated:"""

            if form_validated:
                self.save_model(request, new_object, form, False)
                self.save_related(request, form, formsets, False)
                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)

            PANDA_SKIP_INLINES = """prefixes = {}
            
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)"""

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            prepopulated = dict(inline.get_prepopulated_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'email_enabled': config_value('EMAIL', 'EMAIL_ENABLED')
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(UserProxy, UserModelAdmin)

# Hide sites framework
admin.site.unregister(Site)

class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug')
    prepopulated_fields = { 'slug': ('name', ) }

    def save_model(self, request, obj, form, change):
        """
        On save, update full text metadata of related datasets. 
        """
        if change:
            datasets = list(obj.datasets.all())
            obj.save()

            for dataset in datasets:
                dataset.update_full_text(commit=False)

            solr.commit(settings.SOLR_DATASETS_CORE)
        else:
            obj.save()

    def delete_model(self, request, obj):
        """
        On delete, update full text metadata of related datasets. 
        """
        datasets = list(obj.datasets.all())
        obj.delete()

        for dataset in datasets:
            dataset.update_full_text()

        solr.commit(settings.SOLR_DATASETS_CORE)

admin.site.register(Category, CategoryAdmin)

class TaskStatusAdmin(admin.ModelAdmin):
    fields = ('task_name', 'task_description', 'status', 'message', 'start', 'end', 'traceback', 'creator')
    readonly_fields = ('task_name', 'task_description', 'status', 'message', 'start', 'end', 'traceback', 'creator')
    
    list_display = ('task_name', 'task_description',  'status', 'start', 'end', 'creator')
    list_display_links = ('task_name', 'task_description')
    list_filter = ('status', )

    actions = ['abort_task']

    def get_urls(self):
        urls = super(TaskStatusAdmin, self).get_urls()
        custom_urls = patterns('',
            url(r'^(.+)/abort$',
                self.admin_site.admin_view(self.abort_single),
                name='%s_%s_abort' % (self.model._meta.app_label, self.model._meta.module_name)
            ),
        )

        return custom_urls + urls

    def abort_single(self, request, pk):
        task = get_object_or_404(TaskStatus, pk=pk)

        if task.end:
            self.message_user(request, 'You can not abort a task that has already ended.')
        else:
            task.request_abort()
            self.message_user(request, 'Attempting to abort task.')

        return HttpResponseRedirect(
            reverse('admin:panda_taskstatus_changelist')
        )

    def abort_task(self, request, queryset):
        tasks = list(queryset)

        for task in tasks:
            if task.end:
                self.message_user(request, 'You can not abort tasks that have already ended.')
                return

        for task in tasks:
            task.request_abort()
        
        self.message_user(request, 'Attempting to abort %i task(s).' % len(tasks))

    abort_task.short_description = 'Abort task(s)'

admin.site.register(TaskStatus, TaskStatusAdmin)

admin.site.disable_action('delete_selected')

