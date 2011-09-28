#!/usr/bin/env python

from django import forms

from redd.models import Dataset

class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        widgets = {
            'filepath': forms.HiddenInput(),
        }

