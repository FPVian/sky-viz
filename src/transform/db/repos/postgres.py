from transform.utils.logger import Logger
from transform.db.base_repo import BaseRepository

from sqlalchemy import create_engine, URL

log = Logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class PostgresRepository(BaseRepository):
    '''
    Creates a Postgres connectable and executes database operations.

    unused_settings is added to accept and ignore extra settings
    passed in by the hydra instantiate function.
    '''
    def __init__(self, driver: str, username: str, password: str,
                 host: str, port: int, database: str, **unused_settings):
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
