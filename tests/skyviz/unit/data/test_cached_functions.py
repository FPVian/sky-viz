from flights.db.repos.sqlite import SqliteRepository
from flights.config.settings import s as flights_s
from skyviz.config.settings import s
from database.models import FlightSamples, FlightAggregates
from skyviz.data.cached_functions import Cache

from hydra.utils import instantiate
from sqlalchemy.orm import Session
import polars as pl

import os
import pytest
from datetime import datetime
import pytz


@pytest.fixture
def sqlite_repo():
    '''
    Warning! This will delete a local sqlite database file, if any.
    Make sure environment is set to 'test' in conftest.py
    '''
    try:
        os.remove(flights_s.db.database_path)
    except FileNotFoundError:
        pass
    db: SqliteRepository = instantiate(flights_s.db)
    db.upgrade_db()
    yield db
    os.remove(flights_s.db.database_path)


def test_read_table(sqlite_repo: SqliteRepository):
    '''
    Test that the read_table function reads rows from the database into a polars dataframe.
    '''
    rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=1.1,
            longitude=2.2,
        ),
        FlightSamples(
            icao_id='abc456',
            sample_entry_date_utc=datetime(2023, 6, 10),
            latitude=-3.3,
            longitude=-4.4,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, rows)
    result = Cache.read_table(FlightSamples)
    assert result[0, 0] == 'abc123'
    assert result[1, 0] == 'abc456'


def test_convert_column_to_local_time(sqlite_repo: SqliteRepository):
    '''
    Test that the filter_aggregates_by_num_days function converts utc to local time.
    '''
    sample_time = datetime(2023, 6, 15, 13, 52).replace(tzinfo=pytz.utc)
    rows = [
        FlightAggregates(
            sample_entry_date_utc=sample_time,
            number_of_flights=10,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, rows)
    result = Cache.convert_utc_to_local_time(
        FlightAggregates, FlightAggregates.sample_entry_date_utc.name, 'local').collect()
    assert result.select(pl.col('local')).item() == (
        sample_time.astimezone(pytz.timezone(s.general.time_zone)))


def test_filter_aggregates_by_num_days(sqlite_repo: SqliteRepository):
    '''
    Test that the filter_aggregates_by_num_days function returns
    the correct rows of the flight_aggregates table.
    '''
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    rows = [
        FlightAggregates(
            sample_entry_date_utc=now,
            number_of_flights=10,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 6, 10),
            number_of_flights=20,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, rows)
    result = Cache.filter_flight_aggregates_by_recent_days(1)
    assert result.select(pl.count()).item() == 1
    assert result.select(pl.col(FlightAggregates.number_of_flights.name)).item() == 10
