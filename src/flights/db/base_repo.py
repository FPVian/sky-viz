from flights.utils import logger

from abc import ABC, abstractmethod
from sqlalchemy import Engine
from alembic.config import Config
from alembic import command

log = logger.create(__name__)


class BaseRepository(ABC):
    '''
    See the docs for writing SQL statements with SQLAlchemy 2.0 here:
    https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
    '''
    @abstractmethod
    def __init__(self, alembic_ini_path, alembic_folder_path):
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path
    
    @abstractmethod
    def engine(self) -> Engine:
        pass

    def upgrade_db(self):
        '''
        Upgrades the existing database to the latest version.
        If SQLite is selected, creates a new database if there isn't one already.
        '''
        log.info('upgrading db')
        alembic_config = Config(self.alembic_ini_path)
        alembic_config.set_main_option('script_location', self.alembic_folder_path)
        command.upgrade(alembic_config, 'head')

    def insert_rows(self, rows: list):
        pass