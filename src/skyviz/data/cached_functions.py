from skyviz.config.settings import s
from skyviz.utils import logger
from database.models import Base, FlightAggregates
from skyviz.db.base_repo import BaseRepository

import streamlit as st
import polars as pl
from sqlalchemy import select
from hydra.utils import instantiate

from datetime import timedelta
from datetime import datetime
import pytz

log = logger.create(__name__)

'''
These functions make use of the db repository but must remain separate since the results are cached.

Polars docs: https://pola-rs.github.io/polars/py-polars/html/reference/
'''


class Cache:
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
    def convert_utc_to_local_time(
        table_model: Base, utc_column_name: str, new_column_name: str) -> pl.DataFrame:
        '''
        Converts naive datetime column from UTC to local time and
        returns a dataframe with the new column.
        '''
        log.info(f'converting {utc_column_name} to {s.general.time_zone} time')
        table: pl.DataFrame = Cache.read_table(table_model)
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
        flight_aggregates: pl.DataFrame = Cache.convert_utc_to_local_time(
            FlightAggregates, FlightAggregates.sample_entry_date_utc.name, 'sample_entry_date_ct')
        start_date = datetime.now(tz=pytz.timezone(s.general.time_zone)) - timedelta(days=num_days)
        flight_aggregates = (
            flight_aggregates.filter(pl.col('sample_entry_date_ct') >= start_date)
        )
        log.info(f'returning flight aggregates filtered to last {num_days} days')
        return flight_aggregates
