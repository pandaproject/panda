#!/usr/bin/env python

from tastypie.resources import ModelResource
from redd.models import Dataset

class DatasetResource(ModelResource):
    class Meta:
        queryset = Dataset.objects.all()
        resource_name = 'dataset'

