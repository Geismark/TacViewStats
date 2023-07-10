import logging
from src.utils.configUtils import config
from src.utils.timeUtils import get_timer
from src.utils.logUtils import (
    add_logging_level,
    get_console_logger_config,
    get_file_logger_config,
    setup_config_output_dir,
    prepare_output_directory,
)


class Logger(logging.Logger):
    # https://stackoverflow.com/a/76268417 This saved me.....
    def __init__(self, name, setup_trace=True):
        get_timer()  # placed here to ensure timer starts no matter which module is run
        super().__init__(name, 0)
        # setup new level 'TRACE' @val==5
        if setup_trace:
            add_logging_level("TRACE", 5)
            add_logging_level("DETAIL", 1)

        debug_log1, debug_log2 = [], []

        # setup console logging (allows for logging whilst setting up fileHandler)
        if config.LOGGING.to_console:
            self._console_handler = logging.StreamHandler()
            level, formatter = get_console_logger_config()
            self._console_handler.setLevel(level)
            self._console_handler.setFormatter(formatter)
            self.addHandler(self._console_handler)
        # setup file logging
        if config.LOGGING.to_file:
            output_dir, debug_log1 = setup_config_output_dir()
            output_file_path, debug_log2 = prepare_output_directory(output_dir)
            self._file_handler = logging.FileHandler(filename=output_file_path)
            level, formatter = get_file_logger_config()
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(formatter)
            self.addHandler(self._file_handler)

        for log in debug_log1 + debug_log2:
            logging.Logger.debug(self, log)


logger = Logger(__name__)
