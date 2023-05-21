from flights.config.settings import s
from flights.utils import logger

from sqlalchemy import create_engine

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class Repository:
    def __init__(self):
        self.db_path = s.Database.SQLITE_PATH

    def engine(self):
        log.info('creating sqlite engine')
        return create_engine(f'sqlite:///{self.db_path}', echo=False)
