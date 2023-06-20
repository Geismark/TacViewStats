# TO RUN:
# ...\TacViewStats> python -m unittest src/tests/test_run.py

# ALTERNATIVELY:
# ...\TacViewStats> python -m unittest discover -s src/tests
# this file will not run as it does not start with test*.py

import unittest
from src.tests import (
    test_classes,
    test_dirManager,
    test_fileManager,
    test_fileUtils,
    test_lineHandler,
)

try:
    from dev.dev_testing_vars import dev_verbosity_all, dev_skip_dirs

    import_verbosity = dev_verbosity_all
    import_skip_dirs = dev_skip_dirs
except ImportError:
    import_verbosity = 1
    import_skip_dirs = False


class TestAll(unittest.TestCase):
    def setUp(self) -> None:
        self.verbosity_all = import_verbosity  # 0=quiet, 1=default, 2=verbose
        self.skip_dirs = import_skip_dirs

    # def tearDown(self):
    #     pass

    def test_classes(self):
        classes_suite = unittest.TestLoader().loadTestsFromModule(test_classes)
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(classes_suite)

    def test_dirManager(self):
        if self.skip_dirs:
            return  # FUTUREDO is there an automatic way to test dialog windows?
        dirManager_suite = unittest.TestLoader().loadTestsFromModule(test_dirManager)
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(dirManager_suite)

    def test_fileManager(self):
        fileManager_suite = unittest.TestLoader().loadTestsFromModule(test_fileManager)
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(fileManager_suite)

    # def test_fileUtils(self):
    #     fileUtils_suite = unittest.TestLoader().loadTestsFromModule(test_fileUtils)
    #     unittest.TextTestRunner(verbosity=self.verbosity_all).run(fileUtils_suite)

    # def test_lineHandler(self):
    #     lineHandler_suite = unittest.TestLoader().loadTestsFromModule(test_lineHandler)
    #     unittest.TextTestRunner(verbosity=self.verbosity_all).run(lineHandler_suite)


# https://stackoverflow.com/questions/31559473/run-unittests-from-a-different-file


if __name__ == "__main__":
    unittest.main()
