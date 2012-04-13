#!/usr/bin/env python

import logging
logging.disable(logging.INFO)

from panda.tests.test_admin import TestUserAdmin
from panda.tests.test_api_data import TestDataValidation, TestAPIData 
from panda.tests.test_api_dataset import TestDatasetValidation, TestAPIDataset
from panda.tests.test_api_export import TestAPIExport
from panda.tests.test_api_notification import TestAPINotifications
from panda.tests.test_api_task_status import TestAPITaskStatus
from panda.tests.test_api_data_upload import TestAPIDataUpload
from panda.tests.test_api_related_upload import TestAPIRelatedUpload
from panda.tests.test_api_user import TestUserValidation, TestAPIUser
from panda.tests.test_api_category import TestAPICategories
from panda.tests.test_dataset import TestDataset
from panda.tests.test_data_upload import TestDataUpload
from panda.tests.test_solr import TestSolrJSONEncoder
from panda.tests.test_related_upload import TestRelatedUpload
from panda.tests.test_user import TestUser
from panda.tests.test_utils import TestCSV, TestXLS, TestXLSX, TestTypeCoercion
from panda.tests.test_views import TestLogin, TestActivate

