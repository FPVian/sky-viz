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
        self.db_url = s.Database.POSTGRES_URL

    def engine(self):
        log.info('creating postgres engine')
        return create_engine(self.db_url)
