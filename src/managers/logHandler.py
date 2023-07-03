import os
import logging
from src.utils.configUtils import config
from src.utils.timeUtils import get_date_time


# def log(level, msg):
#     level = level.lower()
#     if level not in ["debug", "info", "warning", "error", "critical"]:
#         raise ValueError(f"Log level is invalid: {level=}")
#     match level:
#         case "debug":
#             pass
#         case "info":
#             pass
#         case "warning":
#             pass
#         case "error":
#             pass
#         case "critical":
#             pass
#     if config.LOGGING.to_file:
#         print(True)


def setup_log_config():
    if not config.LOGGING.to_console:
        config.LOGGING.level = 51  # will ignore all logging calls (critical = 50)
    if not config.LOGGING.to_file:
        config.LOGGING.file_output_dir = None
    else:
        date, time = get_date_time()
        config.LOGGING.file_output_dir = (
            f"{os.getcwd()}{config.LOGGING.file_output_dir}log-{date}-{time}.log"
        )

    logging.basicConfig(
        level=config.LOGGING.level,
        format=config.LOGGING.format,
        datefmt=config.LOGGING.datefmt,
        filename=config.LOGGING.file_output_dir,
    )


# TODO add advanced logging & be able to independently change format and level of console and file
