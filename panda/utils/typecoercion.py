#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, time, datetime

from csvkit.typeinference import NULL_VALUES, TRUE_VALUES, FALSE_VALUES, DEFAULT_DATETIME
from dateutil.parser import parse
from django.utils.translation import ugettext as _

from panda.exceptions import TypeCoercionError

TYPE_NAMES_MAPPING = {
    'unicode': unicode,
    'int': int,
    'bool': bool,
    'float': float,
    'datetime': datetime,
    'date': date,
    'time': time
}

CURRENCY_SYMBOLS_ASCII = '$,'

# Via http://en.wikipedia.org/wiki/Currency_sign
CURRENCY_SYMBOLS_UNICODE_TRANSLATE_TABLE = dict([(ord(c), None) for c in '$,€£₱؋฿₵₡₫ƒ₣₲₴₭ლ₥₦£៛₹₪৳₮₩¥'])

class DataTyper(object):
    """
    A callable object that adds typed columns to a Solr object based on a Dataset schema.
    Along the way it also updates the schema based on the new data.
    """
    def __init__(self, schema):
        self.schema = schema

        # Min/max values for dates/times/datetimes get stored as strings and need to be coerced back
        for n, c in enumerate(self.schema):
            if c['indexed'] and c['type']:
                t = TYPE_NAMES_MAPPING[c['type']]
            
                if t in (date, time, datetime):
                    self.schema[n]['min'] = self.coerce_type(c['min'], datetime)
                    self.schema[n]['max'] = self.coerce_type(c['max'], datetime)

        self.errors = [[] for c in self.schema]

    def __call__(self, data, row):
        """
        Given a Solr data object and a row of data, will ad typed columns to the data
        object and then return it.
        """
        for n, c in enumerate(self.schema):
            if c['indexed'] and c['type']:
                try:
                    t = TYPE_NAMES_MAPPING[c['type']]
                    value = self.coerce_type(row[n], t)
                    data[c['indexed_name']] = value

                    if t in [int, float, date, time, datetime] and value is not None:
                        if c['min'] is None or value < c['min']:
                            self.schema[n]['min'] = value

                        if c['max'] is None or value > c['max']:
                            self.schema[n]['max'] = value
                except TypeCoercionError, e:
                    self.errors[n].append(e)

        return data
    
    def summarize(self):
        """
        Generate a plain-text summary of typing, suitable for an email notification.
        """
        if any([c['indexed'] for c in self.schema]):
            summary = 'Summary of column filters:\n\n'

            for n, c in enumerate(self.schema):
                if c['indexed'] and c['type']:
                    error_count = len(self.errors[n])

                    if not error_count:
                        summary += _('%(name)s: all values succesfully converted to type "%(type)s"\n') \
                            % {'name': c['name'], 'type': c['type']}
                    else:
                        summary += _('%(name)s: failed to convert %(error_count)i values to type "%(type)s"\n') \
                            % {'name': c['name'], 'error_count': error_count, 'type': c['type']}

            return summary
        else:
            return None

    def coerce_type(self, value, normal_type):
        """
        Coerce a single value into a type supported by PANDA.
        
        All one function for performance.
        """
        if isinstance(value, basestring) and value.lower() in NULL_VALUES:
            value = None

        # All types support nulls
        if value is None:
            return None

        try:
            # unicode
            if normal_type is unicode:
                return unicode(value)
            # int
            elif normal_type is int:
                # Filter currency symbols
                if isinstance(value, str):
                    value = value.translate(None, CURRENCY_SYMBOLS_ASCII)
                elif isinstance(value, unicode):
                    value = value.translate(CURRENCY_SYMBOLS_UNICODE_TRANSLATE_TABLE)

                return int(value) 
            # bool
            elif normal_type is bool:
                if isinstance(value, basestring):
                    lcase = value.lower()

                    if lcase in TRUE_VALUES:
                        value = True
                    elif lcase in FALSE_VALUES:
                        value = False
                    else:
                        raise ValueError()

                return bool(value)
            # float
            elif normal_type is float:
                # Filter currency symbols
                if isinstance(value, str):
                    value = value.translate(None, CURRENCY_SYMBOLS_ASCII)
                elif isinstance(value, unicode):
                    value = value.translate(CURRENCY_SYMBOLS_UNICODE_TRANSLATE_TABLE)

                return float(value)
            # date, time, datetime
            elif normal_type in [date, time, datetime]:
                # Don't parse empty strings!
                if not value:
                    raise ValueError()

                try:
                    d = parse(value, default=DEFAULT_DATETIME)
                except OverflowError:
                    raise ValueError()
                except TypeError:
                    raise ValueError()

                return d
        except ValueError:
            raise TypeCoercionError(value, normal_type)

