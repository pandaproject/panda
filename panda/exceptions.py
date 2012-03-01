#!/usr/bin/env python

class DatasetLockedError(Exception):
    """
    Exception raised when a lock can not be acquired on a dataset.
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

