import unittest
from src.managers.logHandler import Logger, logger
from src.utils.configUtils import config
import logging


class TestManagersLogHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_logging_setup(self):
        # ensure TRACE level is setup correctly
        self.assertEqual(logging.TRACE, 5)
        self.assertEqual(logging.DEBUG, 10)
        self.assertEqual(logging.INFO, 20)
        self.assertEqual(logging.WARNING, 30)
        self.assertEqual(logging.ERROR, 40)
        self.assertEqual(logging.CRITICAL, 50)

        config.LOGGING.to_console = False
        config.LOGGING.to_file = False
        empty_logger = Logger("empty_handler", setup_trace=False)

        # ensure no errors when running each level
        empty_logger.trace("5")
        empty_logger.debug("10")
        empty_logger.info("20")
        empty_logger.warning("30")
        empty_logger.error("40")
        empty_logger.critical("50")

    def test_Logger_setup(self):
        # ensure TRACE isn't re-init'd if Logger is called again
        with self.assertRaises(AttributeError):
            _ = Logger(__name__)

        console_file_config_list = [
            [False, False],
            [False, True],
            [True, False],
            [True, True],
        ]
        for config_setting in console_file_config_list:
            config.LOGGING.to_console = config_setting[0]
            config.LOGGING.to_file = config_setting[1]

            test_logger = Logger(__name__, setup_trace=False)
            expected_handlers = [0, 0]  # stream, file
            if config.LOGGING.to_console:
                expected_handlers[0] += 1
            if config.LOGGING.to_file:
                # fileHandler also counts as a streamHandler
                expected_handlers[0] += 1
                expected_handlers[1] += 1
            result_handlers = [0, 0]
            for handler in test_logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    result_handlers[0] += 1
                if isinstance(handler, logging.FileHandler):
                    result_handlers[1] += 1
            self.assertEqual(expected_handlers, result_handlers)
