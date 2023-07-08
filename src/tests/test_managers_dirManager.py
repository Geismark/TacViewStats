import unittest
import os
from src.managers.dirManager import directory_dialog, get_directory, get_files
from src.utils.configUtils import config


class TestDirManager(unittest.TestCase):
    def setUp(self):
        pass

    # def tearDown(self):
    #     pass

    def test_directory_dialog(self):
        if config.DEV_TESTING.skip_dialog:
            return

        cwd_to_test_data = os.getcwd() + "/src/tests/test_data"
        test_dir_file = "TEST_DIR.txt.acmi"
        test_dir_check = "TacViewStats/src/tests/test_data"
        test_dir_file_check = "TacViewStats/src/tests/test_data/TEST_DIR.txt.acmi"

        test_data_dir = directory_dialog(
            dialog_single_file=False, init_dir=cwd_to_test_data
        )
        self.assertTrue(os.path.isdir(test_data_dir))
        self.assertIn(test_dir_check, test_data_dir)

        test_data_file = directory_dialog(
            dialog_single_file=True,
            init_dir=cwd_to_test_data,
            init_file=test_dir_file,
        )
        self.assertTrue(os.path.isfile(test_data_file))
        self.assertIn(test_dir_file_check, test_data_file)

        self.test_dir_file = test_data_file

    def test_get_directory(self):
        cwd = os.getcwd()
        cwd_to_test_data = cwd + "/src/tests/test_data"
        cwd_to_test_data = cwd_to_test_data.replace("\\", "/")
        test_dir_file = "TEST_DIR.txt.acmi"

        self.assertEqual(
            cwd_to_test_data,
            get_directory(
                dir_path=cwd_to_test_data,
            ),
        )
        self.assertEqual(
            cwd_to_test_data + "/" + test_dir_file,
            get_directory(
                dir_path=cwd_to_test_data + "/" + test_dir_file,
            ),
        )

        with self.assertRaises(FileNotFoundError):
            get_directory(" ")
        with self.assertRaises(FileNotFoundError):
            get_directory(cwd + "/intended_error_not_found")

    def test_get_files(self):
        cwd = os.getcwd()
        cwd_to_test_data = cwd + "/src/tests/test_data"
        cwd_to_test_data = cwd_to_test_data.replace("\\", "/")

        files_any, counters = get_files(cwd_to_test_data)
        self.assertEqual(counters, [3, 5, 1, 2], msg=f"{counters=}")
        self.assertEqual(len(files_any), 5)
        file0_name = "/Tacview-20230620-222105-DCS-PG-AA-Trainer-Modern-v2.6.zip.acmi"
        file1_name = "/TEST_DIR.txt.acmi"
        file2_name = "/TEST_ZIP_TRIMMED.mod.zip.acmi"
        file3_name = "/ZIP_TEST.acmi"
        self.assertTrue(
            any(file0_name in file for file in files_any),
            msg=f"test_get_files_0 - {files_any=}",
        )
        self.assertTrue(
            any(file1_name in file for file in files_any),
            msg=f"test_get_files_1 - {files_any=}",
        )
        self.assertTrue(
            any(file2_name in file for file in files_any),
            msg=f"test_get_files_2 - {files_any=}",
        )
        self.assertTrue(
            any(file3_name in file for file in files_any),
            msg=f"test_get_files_3 - {files_any=}",
        )


if __name__ == "__main__":
    unittest.main()
