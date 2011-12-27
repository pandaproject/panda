#!/usr/bin/env python

from redd.tasks.import_file import ImportFileTask
from redd.tasks.import_csv import ImportCSVTask
from redd.tasks.import_xls import ImportXLSTask
from redd.tasks.purge_data import PurgeDataTask

def get_import_task_type_for_upload(upload):
    extension = upload.filename[-4:]

    if extension == '.csv':
        return ImportCSVTask
    elif extension == '.xls':
        return ImportXLSTask

