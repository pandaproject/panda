from django.test.simple import DjangoTestSuiteRunner

class ExistingDatabaseTestRunner(DjangoTestSuiteRunner):
    """
    Simple test runner that uses an existing database.
    """
    def setup_databases(self, **kwargs):
        pass 

    def teardown_databases(self, old_config, **kwargs):
        pass

