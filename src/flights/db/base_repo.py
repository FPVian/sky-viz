from flights.utils import logger
from database.models import Base, FlightSamples, FlightAggregates

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command

from typing import Iterator
from datetime import datetime

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
    def __init__(self, engine: Engine, alembic_ini_path: str, alembic_folder_path: str):
        self.engine = engine
        self.alembic_ini_path = alembic_ini_path
        self.alembic_folder_path = alembic_folder_path

    def upgrade_db(self):
        '''
        Upgrades the existing database to the latest version.
        If SQLite is selected, creates a new database if there isn't one already.
        '''
        log.info('upgrading db')
        alembic_config = Config(self.alembic_ini_path)
        alembic_config.set_main_option('script_location', self.alembic_folder_path)
        command.upgrade(alembic_config, 'head')

    def insert_rows(self, session: Session, rows: Iterator[Base]):
        '''
        Starts and closes a SQLAlchemy session for one-off inserting rows into a table.
        '''
        rows_to_insert = list(rows)
        log.info('inserting %s rows into %s table',
                 len(rows_to_insert), rows_to_insert[0].__tablename__ if rows else None)
        session.add_all(rows_to_insert)
        log.info('inserted all rows')

    def get_new_flight_samples(self, session: Session) -> Iterator[FlightSamples]:
        '''
        Fetches flight sample dates without matching aggregates.
        '''
        log.info('fetching flight samples that need to be aggregated')
        query = (
            select(FlightSamples.sample_entry_date_utc)
            .distinct()
            .join(
                FlightAggregates,
                FlightSamples.sample_entry_date_utc == FlightAggregates.sample_entry_date_utc,
                isouter=True,
                )
            .where(FlightAggregates.sample_entry_date_utc == None)
        )
        unmatched_samples: Iterator[FlightSamples] = session.execute(query)
        log.info('returning flight sample dates for aggregation')
        return unmatched_samples
    
    def count_flight_samples_by_date(self, session: Session, sample_date: datetime) -> int:
        '''
        Counts the number of flight samples for a given date.
        '''
        log.info(f'counting flights in sample entered at: {sample_date}')
        count_result: int = (
            session.query(FlightSamples)
            .where(FlightSamples.sample_entry_date_utc == sample_date)
            .count()
        )
        log.info(f'counted {count_result} flights')
        return count_result
