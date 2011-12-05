#!/usr/bin/env python

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson as json
from south.modelsinspector import add_introspection_rules

class JSONField(models.TextField):
    """
    Store arbitrary JSON in a Model field.
    """
    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """
        Convert string value to JSON after its loaded from the database.
        """
        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_prep_value(self, value):
        """
        Convert our JSON object to a string before being saved.
        """
        if value == "":
            return None

        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_prep_value(value)

    def value_to_string(self, obj):
        """
        Called by the serializer.
        """
        value = self._get_val_from_obj(obj)

        return self.get_db_prep_value(value)

add_introspection_rules([], ["^redd\.fields\.JSONField"])

