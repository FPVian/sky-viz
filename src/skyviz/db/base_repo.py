from skyviz.utils import logger
from database.models import Base

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

log = logger.create(__name__)


class BaseRepository():
    '''
    See the docs for writing SQL statements with SQLAlchemy 2.0 here:
    https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

    Unit of work pattern: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html
    '''
    def __init__(self, engine: Engine):
        self.engine = engine

    def read_table(self, table: Base) -> list[Base]:
        '''
        Starts and closes a SQLAlchemy session for one-off reading all rows in a table.
        '''
        query = select(table)
        log.info(f'Returning all rows from {table.__tablename__} table using query:\n{query}')
        with Session(self.engine) as session:
            all_rows = session.execute(query)
        return all_rows
