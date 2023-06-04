from flights.utils import logger
from flights.db.base_repo import BaseRepository

from sqlalchemy import create_engine

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class SqliteRepository(BaseRepository):
    def __init__(self, database):
        self.db_path = database

    @property
    def engine(self):
        log.info('creating sqlite engine')
        return create_engine(f'sqlite:///{self.db_path}', echo=False)
