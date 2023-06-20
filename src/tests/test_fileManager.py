import unittest
import os
from src.managers.fileManager import is_zip, read_files, process_file


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.test_data_dir = self.cwd + "\\src\\tests\\test_data"
        self.zip_file_name = "TEST_ZIP_TRIMMED.mod.zip.acmi"
        self.unzipped_file_name = "TEST_DIR.txt.acmi"
        self.zip_file_dir = self.test_data_dir + "\\" + self.zip_file_name
        self.unzipped_file_dir = self.test_data_dir + "\\" + self.unzipped_file_name

    # def tearDown(self):
    #     pass
    # C:\Users\Owl\Desktop\Programming\Python\Apps\DCS_Data\TacViewStats\src\tests\test_data
    def test_is_zip(self):
        with self.assertRaises(FileNotFoundError):
            is_zip(self.cwd)
        with self.assertRaises(FileNotFoundError):
            is_zip(" ")
        self.assertFalse(is_zip(self.unzipped_file_dir))
        self.assertTrue(is_zip(self.zip_file_dir))

    # def test_read_files(self):
    #     raise NotImplementedError

    # def test_process_file(self):
    #     raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
