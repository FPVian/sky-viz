from skyviz.config.settings import s
from skyviz.utils.logger import Logger
from database.models import Base, FlightSamples, FlightAggregates
from skyviz.db.base_repo import BaseRepository

import streamlit as st
import polars as pl
import pandas
from sqlalchemy import select
from hydra.utils import instantiate

from datetime import timedelta
from datetime import datetime
import pytz

log = Logger.create(__name__)


class Cache:
    '''
    Queries and transforms data to prepare for visualizations.
    These functions make use of the db repository but must remain separate since the results are cached.

    These methods are organized to cache results that are reused and delay polars execution until needed,
    which sometimes sacrifices readability but maximizes performance so the web app is responsive.
    
    Polars docs: https://pola-rs.github.io/polars/py-polars/html/reference/
    '''
    @st.cache_resource
    def init_db() -> BaseRepository:
        log.info('caching database connection')
        return instantiate(s.db)


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def read_table(table_model: Base) -> pl.DataFrame:
        '''
        Reads an entire table into a polars dataframe.
        '''
        log.info(f'caching {table_model.__tablename__} table')
        db = Cache.init_db()
        table: pl.DataFrame = pl.read_database(select(table_model), db.engine)
        log.info(f'returning {table_model.__tablename__} table')
        return table


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def read_latest_flight_sample() -> pandas.DataFrame:  # pull from RecentFlightSamples
        '''
        Reads the latest sample of flights into a pandas dataframe.

        Return columns: latitude, longitude
        '''
        log.info('caching latest sample in flight_samples table')
        db = Cache.init_db()
        last_sample: pl.DataFrame = Cache.get_last_flight_aggregate()
        last_sample_date: datetime = last_sample.select(
            pl.col(FlightAggregates.sample_entry_date_utc.name)).item()
        query = (
            select(FlightSamples.latitude, FlightSamples.longitude)
            .where(FlightSamples.sample_entry_date_utc == last_sample_date)
        )
        latest_flight_sample: pandas.DataFrame = (
            pl.read_database(query, db.engine)
            .to_pandas(use_pyarrow_extension_array=True)
        )
        log.info('returning latest flight sample')
        return latest_flight_sample


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def convert_utc_to_local_time(
        table_model: Base, utc_column_name: str, new_column_name: str) -> pl.LazyFrame:
        '''
        Converts naive datetime column from UTC to local time and
        returns a dataframe with the new column.
        '''
        log.info(f'converting {utc_column_name} to {s.general.time_zone} time')
        table: pl.LazyFrame = Cache.read_table(table_model).lazy()
        table = (
            table.with_columns(
                pl.col(utc_column_name)
                .dt.replace_time_zone(time_zone='UTC')
                .dt.convert_time_zone(time_zone=s.general.time_zone)
                .alias(new_column_name)
            )
        )
        log.info(f'added column {new_column_name} to {table_model.__tablename__} table')
        return table


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def filter_flight_aggregates_by_recent_days(num_days: int) -> pl.DataFrame:
        '''
        Fetches flight aggregates in local time and filters to a given number of recent days.

        Return dataframe columns: sample_entry_date_utc, number_of_flights, sample_entry_date_ct
        '''
        log.info(f'filtering flight aggregates to last {num_days} days')
        flight_aggregates: pl.LazyFrame = Cache.convert_utc_to_local_time(
            FlightAggregates, FlightAggregates.sample_entry_date_utc.name, 'sample_entry_date_ct')
        start_date = datetime.now(tz=pytz.timezone(s.general.time_zone)) - timedelta(days=num_days)
        flight_aggregates: pl.DataFrame = (
            flight_aggregates.filter(pl.col('sample_entry_date_ct') >= start_date).collect()
        )
        log.info(f'returning flight aggregates filtered to last {num_days} days')
        return flight_aggregates


    def _get_flight_count_last_sample(flight_aggregates: pl.LazyFrame) -> pl.LazyFrame:
        '''
        Fetches the most recent row of a flight_aggregates LazyFrame.

        Return columns: number_of_flights, sample_entry_date_utc
        '''
        log.info('fetching most recent row in flight_aggregates LazyFrame')
        current_flights: pl.LazyFrame = flight_aggregates.select(
                    pl.col(
                        FlightAggregates.number_of_flights.name,
                        FlightAggregates.sample_entry_date_utc.name,
                        )
                    .filter(pl.col(FlightAggregates.sample_entry_date_utc.name) == (
                        pl.max(FlightAggregates.sample_entry_date_utc.name))
                        )
                )
        log.info('returning most recent row in flight_aggregates LazyFrame')
        return current_flights


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def get_last_flight_aggregate() -> pl.DataFrame:
        '''
        Fetches the most recent sample in flight_aggregates.
        '''
        log.info('fetching flight_agreggates for most recent sample')
        flight_aggregates: pl.LazyFrame = Cache.read_table(FlightAggregates).lazy()
        current_flights: pl.DataFrame = Cache._get_flight_count_last_sample(flight_aggregates).collect()
        log.info('returning flight_aggregates most recent sample')
        return current_flights


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def get_current_flights_count() -> int:
        '''
        Fetches the number of flights in the most recent sample.
        '''
        log.info('fetching number of flights in most recent sample')
        last_aggregate: pl.DataFrame = Cache.get_last_flight_aggregate()
        current_flights: int = last_aggregate.select(
            pl.col(FlightAggregates.number_of_flights.name)).item()
        log.info(f'{current_flights} flights in most recent sample')
        return current_flights


    @st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
    def calc_change_in_flights() -> int:
        '''
        Calculates the difference in flights between the most recent sample and the previous sample.
        '''
        log.info('fetching number of flights in last sample')
        flight_aggregates: pl.LazyFrame = Cache.read_table(FlightAggregates).lazy()
        flights_minus_current: pl.LazyFrame = flight_aggregates.select(
            pl.col(FlightAggregates.number_of_flights.name, FlightAggregates.sample_entry_date_utc.name)
            .filter(pl.col(FlightAggregates.sample_entry_date_utc.name) != (
                pl.max(FlightAggregates.sample_entry_date_utc.name))
            )
        )
        previous_flights: int = (
            Cache._get_flight_count_last_sample(flights_minus_current)
            .select(pl.col(FlightAggregates.number_of_flights.name))
            .collect()
            .item()
        )
        log.info(f'{previous_flights} flights in last sample')
        change_in_flights: int = Cache.get_current_flights_count() - previous_flights
        log.info(f'returning change in flights: {change_in_flights}')
        return change_in_flights
