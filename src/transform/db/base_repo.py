from transform.utils.logger import Logger
from database.models import Base, FlightSamples, FlightAggregates, DailyTopAircraft, MonthlyTopFlights

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, Mapped
import polars as pl

from typing import Iterator, Optional
from datetime import datetime, date, timedelta

log = Logger.create(__name__)

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
    
    def count_flight_samples_by_date(self, session: Session, sample_date: datetime) -> int:  # deprecated
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
    
    def filter_table_by_dates(
            self,
            table: Base,
            date_column: Mapped[datetime],
            start_date: datetime,
            end_date: Optional[datetime] = None
    ) -> pl.DataFrame:
        '''
        Queries a table for rows between two dates and returns a dataframe.
        If no end_date is specified, the date column is filtered to match start_date exactly.
        '''
        log.info(f'reading {table.__tablename__} table between {start_date} and {end_date}')
        if end_date is None:
            query = select(table).where(date_column == start_date)
        else:
            query = select(table).where(date_column >= start_date, date_column < end_date)
        table: pl.DataFrame = pl.read_database(query, self.engine)
        log.info(f'returning dataframe filered on {date_column}')
        return table

    def avg_count_aircraft_type_per_sample(
            self, start_date: datetime, end_date: datetime) -> pl.DataFrame:
        '''
        Counts the average number of aircraft for each aircraft type over a range of samples.
        '''
        log.info(f'counting aircraft types per sample between {start_date} and {end_date}')
        query = f'''
            select *,
                row_number() over (order by {DailyTopAircraft.num_per_sample.name} desc)
                as {DailyTopAircraft.usage_rank.name}
            from (
                select 
                    {FlightSamples.aircraft_type.name} as {DailyTopAircraft.aircraft_type.name},
                    count({FlightSamples.aircraft_type.name})
                    /
                    count(distinct {FlightSamples.sample_entry_date_utc.name})
                    as {DailyTopAircraft.num_per_sample.name}
                from {FlightSamples.__tablename__}
                where
                    {FlightSamples.aircraft_type.name} is not null and
                    {FlightSamples.sample_entry_date_utc.name} >= '{start_date}' and
                    {FlightSamples.sample_entry_date_utc.name} < '{end_date}'
                group by {FlightSamples.aircraft_type.name}
                order by {DailyTopAircraft.num_per_sample.name} desc
            ) as avg_count_aircraft_type_per_sample
        '''
        avg_aircraft_by_type: pl.DataFrame = pl.read_database(query, self.engine)
        log.info('returning table of aircraft types averaged per sample')
        return avg_aircraft_by_type
    
    def count_num_flights_by_aircraft_type(self, entry_date: date) -> pl.DataFrame:
        '''
        Counts the number of unique flights for each aircraft type over a day of samples.
        '''
        log.info(f'counting flights for each aircraft type on {entry_date}')
        end_date = entry_date + timedelta(days=1)
        query = f'''
            select *,
                row_number() over (order by {DailyTopAircraft.num_flights.name} desc)
                as {DailyTopAircraft.flights_rank.name}
            from (
                select 
                    {FlightSamples.aircraft_type.name} as {DailyTopAircraft.aircraft_type.name},
                    count(distinct {FlightSamples.flight.name}) as {DailyTopAircraft.num_flights.name}
                from {FlightSamples.__tablename__}
                where
                    {FlightSamples.flight.name} is not null and
                    {FlightSamples.flight.name} not in ('        ', '00000000', 'N       ') and
                    {FlightSamples.aircraft_type.name} is not null and
                    {FlightSamples.sample_entry_date_utc.name} >= '{entry_date}' and
                    {FlightSamples.sample_entry_date_utc.name} < '{end_date}'
                group by {FlightSamples.aircraft_type.name}
                order by {DailyTopAircraft.num_flights.name} desc
            ) as count_num_flights_by_aircraft_type
        '''
        flights_by_aircraft_type: pl.DataFrame = pl.read_database(query, self.engine)
        log.info('returning table of flights by aircraft type')
        return flights_by_aircraft_type
    
    def count_unique_aircraft_by_aircraft_type(
            self, start_date: datetime, end_date: datetime) -> pl.DataFrame:
        '''
        Counts the number of unique aircraft registrations for each aircraft type
        over a range of samples.
        '''
        log.info(f'counting unique aircraft registrations between {start_date} and {end_date}')
        query = f'''
            select *,
                row_number() over (order by {DailyTopAircraft.num_unique_aircraft.name} desc)
                as {DailyTopAircraft.aircraft_rank.name}
            from (
                select 
                    {FlightSamples.aircraft_type.name} as {DailyTopAircraft.aircraft_type.name},
                    count(distinct {FlightSamples.aircraft_registration.name})
                    as {DailyTopAircraft.num_unique_aircraft.name}
                from {FlightSamples.__tablename__}
                where
                    {FlightSamples.aircraft_type.name} is not null and
                    {FlightSamples.sample_entry_date_utc.name} >= '{start_date}' and
                    {FlightSamples.sample_entry_date_utc.name} < '{end_date}'
                group by {FlightSamples.aircraft_type.name}
                order by {DailyTopAircraft.num_unique_aircraft.name} desc
            ) as count_unique_aircraft_by_aircraft_type
        '''
        unique_aircraft_by_type: pl.DataFrame = pl.read_database(query, self.engine)
        log.info('returning table of unique registrations by aircraft type')
        return unique_aircraft_by_type

    def count_flights_per_month(self, month_start_date: date) -> pl.DataFrame:
        '''
        Counts the number of days each flight code is flown over the course of a month.
        '''
        log.info(f'counting unique flights for each day in month starting: {month_start_date}')
        if month_start_date.month < 12:
            end_date = date(month_start_date.year, month_start_date.month+1, 1)
        else:
            end_date = date(month_start_date.year+1, 1, 1)
        query = f'''
            select *,
                dense_rank() over (order by {MonthlyTopFlights.num_days_flown.name} desc)
                as {MonthlyTopFlights.monthly_rank.name}
            from (
                select
                    {FlightSamples.flight.name} as {MonthlyTopFlights.flight.name},
                    count(distinct cast({FlightSamples.sample_entry_date_utc.name} as date))
                    as {MonthlyTopFlights.num_days_flown.name}
                from {FlightSamples.__tablename__}
                where
                    {FlightSamples.flight.name} is not null and
                    {FlightSamples.flight.name} not in ('        ', '00000000', 'N       ') and
                    {FlightSamples.sample_entry_date_utc.name} >= '{month_start_date}' and
                    {FlightSamples.sample_entry_date_utc.name} < '{end_date}'
                group by {FlightSamples.flight.name}
                order by {MonthlyTopFlights.num_days_flown.name} desc
            ) as count_flights_per_month
        '''
        recurring_flights: pl.DataFrame = pl.read_database(query, self.engine)
        log.info('returning table of number of days each flight is flown')
        return recurring_flights
