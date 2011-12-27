#!/usr/bin/env python

from redd.tasks.import_file import ImportFileTask
from redd.tasks.import_csv import ImportCSVTask
from redd.tasks.import_xls import ImportXLSTask
from redd.tasks.purge_data import PurgeDataTask

def get_import_task_type_for_upload(upload):
    data_type = upload.infer_data_type()

    if data_type == 'csv':
        return ImportCSVTask
    elif data_type == 'xls':
        return ImportXLSTask

    return None

