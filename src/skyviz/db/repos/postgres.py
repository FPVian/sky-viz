from skyviz.utils import logger
from skyviz.db.base_repo import BaseRepository

from sqlalchemy import create_engine, URL

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class PostgresRepository(BaseRepository):
    '''
    Creates a Postgres connectable and executes database operations.
    '''
    def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str):
        log.info('instantiating postgres repo')
        db_url = URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        engine = create_engine(db_url)
        super().__init__(engine)
