from src.utils.configUtils import config


def log(level, msg):
    if config.LOGGING.to_file:
        print(True)
