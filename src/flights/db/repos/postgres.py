from flights.config.settings import s
from flights.utils import logger
from flights.db.base_repo import BaseRepository

from sqlalchemy import create_engine, URL

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class PostgresRepository(BaseRepository):
    def __init__(self):
        self.db_url = URL.create(
            drivername='postgresql+psycopg',
            username=s.db.username,
            password=s.db.password,
            host=s.db.host,
            port=s.db.port,
            database=s.db.name
        )

    def engine(self):
        log.info('creating postgres engine')
        return create_engine(self.db_url)
