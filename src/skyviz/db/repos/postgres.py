from flights.utils import logger
from flights.db.base_repo import BaseRepository

from sqlalchemy import create_engine, URL

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class PostgresRepository(BaseRepository):
    def __init__(self, driver, username, password, host, port, database):
        self.db_url = URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )

    @property
    def engine(self):
        log.info('creating postgres engine')
        return create_engine(self.db_url)
