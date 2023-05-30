from flights.config.settings import s
from flights.utils import logger

from sqlalchemy import create_engine, URL

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class Repository:
    def __init__(self):
        self.db_url = URL.create(
            drivername='postgresql+psycopg',
            username=s.Database.Postgres.USERNAME,
            password=s.Database.Postgres.PASSWORD,
            host=s.Database.Postgres.HOST,
            port=s.Database.Postgres.PORT,
            database=s.Database.Postgres.DB_NAME
        )

    def engine(self):
        log.info('creating postgres engine')
        return create_engine(self.db_url)
