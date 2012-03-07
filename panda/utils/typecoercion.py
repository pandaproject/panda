#!/usr/bin/env python

import datetime

from csvkit.typeinference import NULL_VALUES, TRUE_VALUES, FALSE_VALUES, DEFAULT_DATETIME
from dateutil.parser import parse

from panda.exceptions import TypeCoercionError

def coerce_type(value, normal_type):
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
                    return None

            return bool(value)
        # float
        elif normal_type is float:
            return float(value)
        # date, time, datetime
        elif normal_type in [datetime.date, datetime.time, datetime.datetime]:
            try:
                d = parse(value, default=DEFAULT_DATETIME)
            except OverflowError:
                raise ValueError()
            except TypeError:
                raise ValueError()

            return d
    except ValueError:
        raise TypeCoercionError(value, normal_type)

