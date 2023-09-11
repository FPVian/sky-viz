from flights.utils import logger
from flights.db.base_repo import BaseRepository

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
    def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str,
                 alembic_ini_path: str, alembic_folder_path: str, **unused_settings):
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
        super().__init__(engine, alembic_ini_path, alembic_folder_path)
