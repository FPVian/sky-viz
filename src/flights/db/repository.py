from config.settings import s
from config.logger import Logger
from database.interface import BaseInterface
from database.models import Base

from hydra.utils import instantiate
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from typing import Iterator

log = Logger.create(__name__)

'''
See the docs for writing SQL statements with SQLAlchemy 2.0 here:
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

Unit of work pattern: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html
'''


class DbRepo():
    '''
    Instantiates the database connectable and provides methods to interact with the database.
    '''
    def __init__(self):
        interface: BaseInterface = instantiate(s.db)
        self.engine: Engine = interface.engine
        self.upgrade_db = interface.upgrade_db

    def insert_rows(self, session: Session, rows: Iterator[Base]):
        '''
        Inserts rows into a mapped sqlalchemy table.
        '''
        rows_to_insert = list(rows)
        log.info('inserting %s rows into %s table',
                 len(rows_to_insert), rows_to_insert[0].__tablename__ if rows else None)
        session.add_all(rows_to_insert)
        log.info('inserted all rows')
