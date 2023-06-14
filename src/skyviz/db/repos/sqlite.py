from skyviz.utils import logger
from skyviz.db.base_repo import BaseRepository

from sqlalchemy import create_engine

log = logger.create(__name__)

'''
SQLAlchemy docs for engine configuration:
https://docs.sqlalchemy.org/en/20/core/engines.html
'''


class SqliteRepository(BaseRepository):
    '''
    Creates a Sqlite connectable and executes database operations. 
    '''
    def __init__(self, database_path: str):
        log.info('instantiating sqlite repo')
        engine = create_engine(f'sqlite:///{database_path}', echo=False)
        super().__init__(engine)
