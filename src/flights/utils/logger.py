from flights.config.settings import s

import logging
from logging import handlers
import os

'''
logging docs: https://docs.python.org/3/howto/logging.html#loggers
'''


def create(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(s.logs.level)

    if s.logs.log_to_file:
        os.makedirs(s.logs.path, exist_ok=True)
        file_handler = handlers.RotatingFileHandler(
            filename=s.logs.file_path,
            maxBytes=s.logs.bytes_per_file,
            backupCount=s.logs.number_of_backups
        )
        file_handler.setLevel(s.logs.level)
        file_formatter = logging.Formatter(s.logs.file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    if s.logs.log_to_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(s.logs.level)
        stream_formatter = logging.Formatter(s.logs.stream_format)
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    return logger
