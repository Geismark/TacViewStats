import unittest
import os
from src.utils.logUtils import (
    add_logging_level,
    get_console_logger_config,
    get_file_logger_config,
    setup_config_output_dir,
    prepare_output_directory,
    get_log_files,
)
import logging
from src.utils.configUtils import config
from src.managers.logHandler import Logger, logger
from glob import glob


class TestUtilsLogUtils(unittest.TestCase):
    def setUp(self):
        config.LOGGING.to_console = True
        config.LOGGING.to_file = False
        config.LOGGING.level = 1
        self.empty_logger = Logger("empty_utils", setup_trace=False)
        self.cwd = os.getcwd()
        self.testing_dir = self.cwd + "/testing_logs"

    def tearDown(self):
        if os.path.isdir(self.testing_dir):
            for file in os.listdir(self.testing_dir):
                os.remove(f"{self.testing_dir}/{file}")
            os.rmdir(self.testing_dir)

    def test_add_logging_level(self):
        # ensure adding new level works as intended
        add_logging_level("DETAILS", 2, "dots")
        self.assertEqual(logging.DETAILS, 2)
        self.empty_logger.dots("not shown")
        # ensure levelName is capitalised
        with self.assertRaises(ValueError):
            add_logging_level("detail", 1)
        # ensure levelName is novel
        with self.assertRaises(AttributeError):
            add_logging_level("DEBUG", 1)
        # ensure methodName is novel
        with self.assertRaises(AttributeError):
            add_logging_level("DETAIL", 1, "dots")
        # ensure methodName is novel to logger
        with self.assertRaises(AttributeError):
            add_logging_level("NOVEL", 1, "trace")
        # ensure logging/logger doesn't allow unknown method names
        with self.assertRaises(AttributeError):
            self.empty_logger.unknown("unknown")

    def test_get_console_logger_config(self):
        config.LOGGING.to_console = False
        config.LOGGING.level = 5
        config.LOGGING.format = "%(asctime)s %(levelname)s - %(message)s"
        config.LOGGING.datefmt = "%H:%M:%S"

        config.CONSOLE_LOGGING.level = None
        config.CONSOLE_LOGGING.format = None
        config.CONSOLE_LOGGING.datefmt = None

        with self.assertRaises(ValueError):
            get_console_logger_config()

        config.LOGGING.to_console = True
        level, formatter = get_console_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.CONSOLE_LOGGING.level = 10
        config.CONSOLE_LOGGING.format = None
        config.CONSOLE_LOGGING.datefmt = None
        level, formatter = get_console_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.CONSOLE_LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.CONSOLE_LOGGING.level = None
        config.CONSOLE_LOGGING.format = "%(asctime)s"
        config.CONSOLE_LOGGING.datefmt = None
        level, formatter = get_console_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.CONSOLE_LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.CONSOLE_LOGGING.level = None
        config.CONSOLE_LOGGING.format = None
        config.CONSOLE_LOGGING.datefmt = "%S:%M:%H"
        level, formatter = get_console_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.CONSOLE_LOGGING.datefmt)

        config.CONSOLE_LOGGING.level = 10
        config.CONSOLE_LOGGING.format = "%(asctime)s"
        config.CONSOLE_LOGGING.datefmt = "%S:%M:%H"
        level, formatter = get_console_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.CONSOLE_LOGGING.level)
        self.assertEqual(formatter._fmt, config.CONSOLE_LOGGING.format)
        self.assertEqual(formatter.datefmt, config.CONSOLE_LOGGING.datefmt)

    def test_get_file_logger_config(self):
        config.LOGGING.to_file = False
        config.LOGGING.level = 5
        config.LOGGING.format = "%(asctime)s %(levelname)s - %(message)s"
        config.LOGGING.datefmt = "%H:%M:%S"

        config.FILE_LOGGING.level = None
        config.FILE_LOGGING.format = None
        config.FILE_LOGGING.datefmt = None

        with self.assertRaises(ValueError):
            get_file_logger_config()

        config.LOGGING.to_file = True
        level, formatter = get_file_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.FILE_LOGGING.level = 10
        config.FILE_LOGGING.format = None
        config.FILE_LOGGING.datefmt = None
        level, formatter = get_file_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.FILE_LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.FILE_LOGGING.level = None
        config.FILE_LOGGING.format = "%(asctime)s"
        config.FILE_LOGGING.datefmt = None
        level, formatter = get_file_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.FILE_LOGGING.format)
        self.assertEqual(formatter.datefmt, config.LOGGING.datefmt)

        config.FILE_LOGGING.level = None
        config.FILE_LOGGING.format = None
        config.FILE_LOGGING.datefmt = "%S:%M:%H"
        level, formatter = get_file_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.LOGGING.level)
        self.assertEqual(formatter._fmt, config.LOGGING.format)
        self.assertEqual(formatter.datefmt, config.FILE_LOGGING.datefmt)

        config.FILE_LOGGING.level = 10
        config.FILE_LOGGING.format = "%(asctime)s"
        config.FILE_LOGGING.datefmt = "%S:%M:%H"
        level, formatter = get_file_logger_config()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertEqual(level, config.FILE_LOGGING.level)
        self.assertEqual(formatter._fmt, config.FILE_LOGGING.format)
        self.assertEqual(formatter.datefmt, config.FILE_LOGGING.datefmt)

    def test_setup_config_output_dir(self):
        # check directory found from project
        config.FILE_LOGGING.file_output_dir = "/outputs/"
        file_path, _ = setup_config_output_dir()
        self.assertEqual(file_path, self.cwd + "/outputs/")

        # check directory is found from root
        config.FILE_LOGGING.file_output_dir = self.cwd
        file_path, _ = setup_config_output_dir()
        self.assertEqual(file_path, self.cwd)

        # check directory returns to default when not found
        config.FILE_LOGGING.file_output_dir = "/__dir_does_not_exist__/"
        file_path, _ = setup_config_output_dir()
        self.assertEqual(file_path, self.cwd + "/outputs/")

    def test_prepare_output_directory(self):
        with self.assertRaises(TypeError):
            prepare_output_directory(2)
        with self.assertRaises(ValueError):
            prepare_output_directory("_not_a_directory_")

        config.FILE_LOGGING.max_output_files = 3
        self.make_file_num = 5
        self.setup_testing_logs_dir()

        file_name, logs = prepare_output_directory(self.testing_dir)
        file_name = file_name.replace("\\", "/").split("/")[-1]
        self.assertTrue(file_name.startswith("log-"), f"{file_name=}")
        self.assertTrue(file_name.endswith(".log"), f"{file_name=}")
        self.assertEqual(len(logs), 4)

        remaining_files = os.listdir(self.testing_dir)
        self.assertIn("random_file.log", remaining_files, f"{remaining_files=}")
        self.assertIn("text.txt", remaining_files)
        names = [
            f"log-{i}.log"
            for i in range(config.FILE_LOGGING.max_output_files, self.make_file_num)
        ]

        for rf in remaining_files:
            if rf.startswith("log-"):
                self.assertIn(rf, names)

        config.FILE_LOGGING.max_output_files = 10
        file_name, logs2 = prepare_output_directory(self.testing_dir)
        self.assertEqual(remaining_files, os.listdir(self.testing_dir))
        self.assertEqual(len(logs2), 0)

    def test_get_log_files(self):
        self.make_file_num = 5
        self.setup_testing_logs_dir()
        solo_file = get_log_files(f"{self.testing_dir}/log-0.log")
        self.assertEqual(solo_file, [f"{self.testing_dir}/log-0.log"])
        multi_files = get_log_files(self.testing_dir)
        for i, f in enumerate(multi_files):
            multi_files[i] = f.replace("\\", "/")
        self.assertEqual(len(multi_files), self.make_file_num + 2)
        for i in range(self.make_file_num):
            self.assertIn(
                f"{self.testing_dir}/log-{i}.log".replace("\\", "/"), multi_files
            )
        self.assertIn(
            f"{self.testing_dir}/random_file.log".replace("\\", "/"), multi_files
        )
        self.assertIn(f"{self.testing_dir}/text.txt".replace("\\", "/"), multi_files)

    def setup_testing_logs_dir(self):
        if os.path.isdir(self.testing_dir):
            raise ValueError("Log Testing Directory already exists")
        os.mkdir(self.testing_dir)
        for i in range(self.make_file_num):
            with open(f"{self.testing_dir}/log-{i}.log", "w") as file:
                file.write(str(i))
        with open(f"{self.testing_dir}/random_file.log", "w") as file:
            file.write("blank")
        with open(f"{self.testing_dir}/text.txt", "w") as file:
            file.write("text")
