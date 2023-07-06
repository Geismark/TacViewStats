import logging
import os
import re
import glob
from src.utils.timeUtils import get_date_time
from src.utils.configUtils import config


def add_logging_level(levelName, levelNum, methodName=None):
    # https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility
    # https://stackoverflow.com/a/35804945
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if levelName != levelName.upper():
        raise ValueError(f"levelName must be uppercase: {levelName=}")

    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def get_console_logger_config():
    if not config.LOGGING.to_console:
        raise ValueError("Console logging config run when to_console != True")

    if config.CONSOLE_LOGGING.level:
        level = config.CONSOLE_LOGGING.level
    else:
        level = config.LOGGING.level

    if config.CONSOLE_LOGGING.format:
        fmt = config.CONSOLE_LOGGING.format
    else:
        fmt = config.LOGGING.format
    if config.CONSOLE_LOGGING.datefmt:
        datefmt = config.CONSOLE_LOGGING.datefmt
    else:
        datefmt = config.LOGGING.datefmt
    formatter = logging.Formatter(fmt, datefmt)

    return level, formatter


def get_file_logger_config():
    if not config.LOGGING.to_file:
        raise ValueError("File logging config run when to_file != True")

    if config.FILE_LOGGING.level:
        level = config.FILE_LOGGING.level
    else:
        level = config.LOGGING.level

    if config.FILE_LOGGING.format:
        fmt = config.FILE_LOGGING.format
    else:
        fmt = config.LOGGING.format
    if config.FILE_LOGGING.datefmt:
        datefmt = config.FILE_LOGGING.datefmt
    else:
        datefmt = config.LOGGING.datefmt
    formatter = logging.Formatter(fmt, datefmt)

    return level, formatter


def setup_config_output_dir():
    debug_logs = []
    file_path = config.FILE_LOGGING.file_output_dir
    if os.path.isdir(f"{os.getcwd()}{file_path}"):
        # if config path is from project dir
        file_path = f"{os.getcwd()}{file_path}"
    elif os.path.isdir(file_path):
        # if config path is from root
        pass
    else:
        debug_logs.append(
            f"Config Output Directory cannot be found:\n\t{file_path=}\n\tUsing default output dir."
        )
        file_path = f"{os.getcwd()}/outputs/"
    debug_logs.append(f"Config logging output file directory: {file_path}")
    config.FILE_LOGGING.file_output_dir = file_path
    return file_path, debug_logs


def prepare_output_directory(output_dir: str):
    debug_logs = []
    print(f"{output_dir=}")
    if not isinstance(output_dir, str):
        raise TypeError(f"Output directory is not a string: {output_dir=}")
    elif not os.path.isdir(output_dir):
        raise ValueError(f"Output directory is not a directory: {output_dir=}")
    all_files = get_log_files(output_dir)
    log_files = []
    for file in all_files:
        file_name = re.split(r"[\\/]", file)[-1]
        if (
            file_name.endswith(".log")
            and file_name.startswith("log-")
            and os.path.isfile(file)
        ):
            log_files.append(file)
    if len(log_files) >= config.FILE_LOGGING.max_output_files:
        modified_timestamps = {}
        for file in log_files:
            mod_time = os.path.getmtime(file)
            modified_timestamps[file] = mod_time
        sorted_timestamps = sorted(modified_timestamps.items(), key=lambda x: x[1])
        files_to_delete = len(log_files) - config.FILE_LOGGING.max_output_files + 1
        if (
            files_to_delete > len(log_files)
            or config.FILE_LOGGING.max_output_files == 0
        ):
            files_to_delete = len(log_files)
        debug_logs.append(
            f"Output directory has too many log files, attempting to remove oldest {files_to_delete} log files."
        )
        for i in range(files_to_delete):
            delete_file = sorted_timestamps[i][0]
            os.remove(delete_file)
            debug_logs.append(f"Deleted old log file: {delete_file}")

    date, time = get_date_time()
    config.FILE_LOGGING.file_output_dir = (
        f"{config.FILE_LOGGING.file_output_dir}log-{date}-{time}.log"
    )
    return config.FILE_LOGGING.file_output_dir, debug_logs


# near identical to dirManager.get_files() BUT needed to initialise logger
def get_log_files(folder_dir: str):
    if os.path.isfile(folder_dir):
        files = [folder_dir]
    else:
        files = glob.glob(f"{folder_dir}/*.*")  # lists all files in dir

    return files
