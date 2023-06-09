from flights.utils import logger
from flights.db.base_repo import BaseRepository

from sqlalchemy import create_engine, Engine
from alembic.config import Config
from alembic import command

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html

Alembic docs for programmatic usage:
https://alembic.sqlalchemy.org/en/latest/api/commands.html#alembic.command.upgrade
'''


class SqliteRepository(BaseRepository):
    def __init__(self, database_path: str, alembic_ini_path: str, alembic_folder_path: str):
        log.info('instantiating sqlite repo')
        self.db_path = database_path
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path

    @property
    def engine(self) -> Engine:
        log.info('creating sqlite engine')
        return create_engine(f'sqlite:///{self.db_path}', echo=False)
