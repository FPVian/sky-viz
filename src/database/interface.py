from config.logger import Logger

from sqlalchemy import Engine, create_engine, URL
from alembic.config import Config
from alembic import command

log = Logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class BaseInterface():
    '''
    Base class for database interfaces.
    '''
    def __init__(self, engine: Engine, alembic_ini_path: str, alembic_folder_path: str):
        self.engine = engine
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path

    def upgrade_db(self):
        '''
        Upgrades the existing database to the latest version.
        If SQLite is selected, creates a new database if there isn't one already.
        '''
        log.info('upgrading db, if necessary')
        alembic_config = Config(self.alembic_ini_path)
        alembic_config.set_main_option('script_location', self.alembic_folder_path)
        command.upgrade(alembic_config, 'head')
        log.info('db is now up to date')


class PostgresInterface(BaseInterface):
    '''
    Creates a Postgres connectable.

    unused_settings is added to accept and ignore extra settings
    passed in by the hydra instantiate function.
    '''
    def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str,
                 alembic_ini_path: str, alembic_folder_path: str, **unused_settings):
        log.info('instantiating postgres interface')
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
        log.info('postgres interface instantiated')


class SqliteInterface(BaseInterface):
    '''
    Creates a Sqlite connectable.
    '''
    def __init__(self, database_path: str, alembic_ini_path: str, alembic_folder_path: str):
        log.info('instantiating sqlite interface')
        engine = create_engine(f'sqlite:///{database_path}', echo=False)
        super().__init__(engine, alembic_ini_path, alembic_folder_path)
        log.info('sqlite interface instantiated')
