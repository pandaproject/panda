#!/usr/bin/env python

class DataImportError(Exception):
    """
    Exception raised when a DataImport fails synchronously
    due to an unsupported file type, mismatched columns, etc.
    """
    pass

