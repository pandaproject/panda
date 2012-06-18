#!/usr/bin/env python

from panda.tasks.export_csv import ExportCSVTask
from panda.tasks.export_search import ExportSearchTask
from panda.tasks.import_csv import ImportCSVTask
from panda.tasks.import_xls import ImportXLSTask
from panda.tasks.import_xlsx import ImportXLSXTask
from panda.tasks.purge_data import PurgeDataTask
from panda.tasks.purge_orphaned_uploads import PurgeOrphanedUploadsTask
from panda.tasks.reindex import ReindexTask
from panda.tasks.run_admin_alerts import RunAdminAlertsTask
from panda.tasks.run_subscriptions import RunSubscriptionsTask

TASKS_BY_TYPE = {
    'csv': ImportCSVTask,
    'xls': ImportXLSTask,
    'xlsx': ImportXLSXTask
}

def get_import_task_type_for_upload(upload):
    try:
        return TASKS_BY_TYPE[upload.data_type]
    except KeyError:
        return None

