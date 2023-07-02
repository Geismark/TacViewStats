import unittest
import os
from src.utils.config import Config

import configparser


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.correct_config_file = """
[TEST]
test_bool = true
test_int = 1
test_str = test
        """

        self.incorrect_config_file = """
[TEST]
test_bool true
test_int = 1
test_str = test
"""

    def test_correct_build(self):
        config = Config(self.correct_config_file)

        self.assertTrue(hasattr(config, "TEST"))

        self.assertTrue(config.TEST.test_bool)
        self.assertIsInstance(config.TEST.test_bool, bool)

        self.assertEqual(config.TEST.test_int, 1)
        self.assertIsInstance(config.TEST.test_int, int)

        self.assertEqual(config.TEST.test_str, "test")
        self.assertIsInstance(config.TEST.test_str, str)

        # Check that there are no other attributes
        self.assertEqual(len(config.__dict__), 1)
        self.assertEqual(len(config.TEST.__dict__), 3)

    def test_incorrect_build(self):
        with self.assertRaises(configparser.ParsingError):
            Config(self.incorrect_config_file)
