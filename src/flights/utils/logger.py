from flights.config.settings import s

import logging
from logging import handlers

'''
logging docs: https://docs.python.org/3/howto/logging.html#loggers
'''


def create(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(s.Logs.LEVEL)

    file_handler = handlers.RotatingFileHandler(
        filename=s.Logs.FILE_PATH,
        maxBytes=s.Logs.BYTES_PER_FILE,
        backupCount=s.Logs.NUMBER_OF_BACKUPS
        )
    file_handler.setLevel(s.Logs.LEVEL)
    file_formatter = logging.Formatter(s.Logs.FILE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    if s.Logs.LOG_TO_CONSOLE is False:
        return logger

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(s.Logs.LEVEL)
    stream_formatter = logging.Formatter(s.Logs.STREAM_FORMAT)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    return logger
