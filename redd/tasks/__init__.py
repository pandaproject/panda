#!/usr/bin/env python

from redd.tasks.export_csv import ExportCSVTask
from redd.tasks.import_csv import ImportCSVTask
from redd.tasks.import_xls import ImportXLSTask
from redd.tasks.import_xlsx import ImportXLSXTask
from redd.tasks.purge_data import PurgeDataTask

TASKS_BY_TYPE = {
    'csv': ImportCSVTask,
    'xls': ImportXLSTask,
    'xlsx': ImportXLSXTask
}

def get_import_task_type_for_upload(upload):
    data_type = upload.infer_data_type()

    try:
        return TASKS_BY_TYPE[data_type]
    except KeyError:
        return None

