from flights.utils import logger
from flights.db.base_repo import BaseRepository

from sqlalchemy import create_engine, URL, Engine

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class PostgresRepository(BaseRepository):
    def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str,
                 alembic_ini_path: str, alembic_folder_path: str):
        log.info('instantiating postgres repo')
        self.db_url = URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path

    @property
    def engine(self) -> Engine:
        log.info('creating postgres engine')
        return create_engine(self.db_url)
