#!/usr/bin/env python

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

