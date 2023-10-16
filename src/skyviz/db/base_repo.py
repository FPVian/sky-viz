from skyviz.utils import logger
from database.models import Base

from sqlalchemy import Engine, select
from sqlalchemy.orm import Mapped

from datetime import datetime, timedelta

log = logger.create(__name__)
'''
See the docs for writing SQL statements with SQLAlchemy 2.0 here:
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

Unit of work pattern: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html
'''


class BaseRepository():
    '''
    Base class for database interfaces.
    '''
    def __init__(self, engine: Engine):
        self.engine = engine

    def calc_minutes_since_last_update(self, session, date_column: Mapped) -> float:
        '''
        Fetches the latest row in a table using the date_column,
        then calculates the time in minutes between the latest date and now.
        '''
        log.info(f'fetching most recent date in {date_column}')
        sql_query = select(date_column).order_by(date_column.desc()).limit(1)
        latest_date: datetime = session.execute(sql_query).scalar_one_or_none()
        log.info(f'{date_column} last updated: {latest_date}')
        time_since_last_update: timedelta = datetime.utcnow() - latest_date
        minutes_since_last_update: float = round(time_since_last_update.total_seconds() / 60, 1)
        log.info(f'calculated {minutes_since_last_update} minutes since last update')
        return minutes_since_last_update
    
    def count_total_rows(self, session, table_model: Base) -> int:
        '''
        Counts the number of rows in a table.
        '''
        log.info(f'counting rows in {table_model.__tablename__} table')
        count_result: int = session.query(table_model).count()
        log.info(f'counted {count_result} rows')
        return count_result

    def count_distinct(self, session, column: Mapped) -> int:  # deprecated due to slow performance
        '''
        Counts the number of distinct values in a single column.
        '''
        log.info(f'counting distinct rows using table.column: {column}')
        count_result: int = session.query(column).distinct().count()
        log.info(f'counted {count_result} rows')
        return count_result
