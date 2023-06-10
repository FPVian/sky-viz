from flights.utils import logger
from database.models import Base

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command

from abc import ABC, abstractmethod

log = logger.create(__name__)


class BaseRepository(ABC):
    '''
    See the docs for writing SQL statements with SQLAlchemy 2.0 here:
    https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

    Unit of work pattern: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html
    '''
    @abstractmethod
    def __init__(self, alembic_ini_path, alembic_folder_path):
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path
    
    @property
    @abstractmethod
    def engine(self) -> Engine:
        '''
        Creates a SQLAlchemy engine for connecting to the database.
        '''
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

    def insert_rows(self, rows: list[Base]):
        '''
        Starts and closes a SQLAlchemy session for one-off inserting rows into a table.
        '''
        log.info(f'inserting {len(rows)} rows into {rows[0].__tablename__}')
        with Session(self.engine) as session, session.begin():
            session.add_all(rows)
