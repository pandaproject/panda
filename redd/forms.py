#!/usr/bin/env python

from django.forms import ModelForm

from redd.models import Upload

class UploadForm(ModelForm):
    class Meta:
        model = Upload

