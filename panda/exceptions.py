#!/usr/bin/env python
from django.utils.translation import ugettext as _

class DatasetLockedError(Exception):
    """
    Exception raised when a lock can not be acquired on a dataset.
    """
    pass

class DataUploadNotDeletable(Exception):
    """
    Exception raised when a DataUpload can not be deleted.
    """
    pass

class DataSamplingError(Exception):
    """
    Exception raised when data can't be sampled from a file,
    such as when unexpected encodings are encountered.
    """
    pass

class DataImportError(Exception):
    """
    Exception raised when a DataImport fails synchronously
    due to an unsupported file type, mismatched columns, etc.
    """
    pass

class NotSniffableError(Exception):
    """
    Exception raised when a file's dialect could not be inferred
    automatically.
    """
    pass

class TypeInferenceError(Exception):
    """
    Exception raised when a column's type can not be inferred.
    """
    pass

class TypeCoercionError(Exception):
    """
    Exception raised when a value can not be coerced to a given type.
    """
    def __init__(self, value, normal_type):
        self.value = value
        self.normal_type = normal_type
        msg = _('Unable to convert "%(value)s" to type %(normal_type)s') \
            % {'value': value, 'normal_type': normal_type}
        super(TypeCoercionError, self).__init__(value, normal_type)

