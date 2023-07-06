# TO RUN:

# RECOMMENDED:
# ...\TacViewStats> poetry run pytest

# ALTERNATIVE 1:
# ...\TacViewStats> python -m unittest src/tests/run_tests.py
# ALTERNATIVE 2:
# ...\TacViewStats> python -m unittest discover -s src/tests
# this file will not run as it does not start with test*.py

import unittest

from src.tests import (
    test_managers_dirManager,
    test_managers_fileManager,
    test_managers_lineHandler,
    test_utils_fileUtils,
    test_classes_FileData,
    test_classes_DCSObject,
    test_classes_DCSEvent,
    test_utils_coordUtils,
)

from src.utils.configUtils import config


class TestAll(unittest.TestCase):
    def setUp(self) -> None:
        self.verbosity_all = (
            config.DEV_TESTING.verbosity_level
        )  # 0=quiet, 1=default, 2=verbose

    # def tearDown(self):
    #     pass

    def test_all(self):
        ############################# classes #############################
        # src/classes/DCSEvent.py
        DCSEvent_suite = unittest.TestLoader().loadTestsFromModule(
            test_classes_DCSEvent
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(DCSEvent_suite)
        # src/classes/DCSObject.py
        DCSObject_suite = unittest.TestLoader().loadTestsFromModule(
            test_classes_DCSObject
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(DCSObject_suite)
        # src/classes/FileData.py
        FileData_suite = unittest.TestLoader().loadTestsFromModule(
            test_classes_FileData
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(FileData_suite)
        ############################# classes #############################

        ############################# managers #############################
        # src/managers/dirManager.py
        # FUTUREDO is there an automatic way to test dialog windows?
        dirManager_suite = unittest.TestLoader().loadTestsFromModule(
            test_managers_dirManager
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(dirManager_suite)
        # src/managers/fileManager.py
        fileManager_suite = unittest.TestLoader().loadTestsFromModule(
            test_managers_fileManager
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(fileManager_suite)
        # src/managers/lineHandler.py
        lineHandler_suite = unittest.TestLoader().loadTestsFromModule(
            test_managers_lineHandler
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(lineHandler_suite)
        ############################# managers #############################

        ############################# utils #############################
        # src/utils/coordUtils.py
        coordUtils_suite = unittest.TestLoader().loadTestsFromModule(
            test_utils_coordUtils
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(coordUtils_suite)
        # src/utils/fileUtils.py
        fileUtils_suite = unittest.TestLoader().loadTestsFromModule(
            test_utils_fileUtils
        )
        unittest.TextTestRunner(verbosity=self.verbosity_all).run(fileUtils_suite)
        # src/utils/mathUtils.py
        # src/utils/performance.py
        ############################# utils #############################

        ############################# data #############################
        # src/data/acmiAttrDicts.py
        ############################# data #############################


# https://stackoverflow.com/questions/31559473/run-unittests-from-a-different-file


if __name__ == "__main__":
    unittest.main()
