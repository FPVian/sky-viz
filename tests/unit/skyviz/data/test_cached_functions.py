from database.interface import SqliteInterface
from config.settings import s
from database.models import FlightSamples, FlightAggregates
from skyviz.data.cached_functions import Cache

from hydra.utils import instantiate
from sqlalchemy.orm import Session
import polars as pl
import pandas

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
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
    db: SqliteInterface = instantiate(s.db)
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


def test_read_table(sqlite_repo: SqliteInterface):
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
        session.add_all(rows)
    result = Cache.read_table(FlightSamples)
    assert result[0, 0] == 'abc123'
    assert result[1, 0] == 'abc456'


def test_read_latest_flight_sample(sqlite_repo: SqliteInterface):
    '''
    Test that the read_latest_flight_sample function returns the latest flight sample
    based on the flight_aggregates table, as a pandas dataframe.
    '''
    rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 5),
            latitude=1.1,
            longitude=2.2,
        ),
        FlightSamples(
            icao_id='abc456',
            sample_entry_date_utc=datetime(2023, 6, 10),
            latitude=-3.3,
            longitude=-4.4,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2023, 6, 10),
            number_of_flights=20,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result: pandas.DataFrame = Cache.read_latest_flight_sample()
    assert result[FlightSamples.latitude.name].item() == -3.3
    assert result[FlightSamples.longitude.name].item() == -4.4


def test_convert_utc_to_local_time(sqlite_repo: SqliteInterface):
    '''
    Test that the convert_utc_to_local_time function converts utc to local time.
    '''
    sample_time = datetime(2023, 6, 15, 13, 52).replace(tzinfo=pytz.utc)
    rows = [
        FlightAggregates(
            sample_entry_date_utc=sample_time,
            number_of_flights=10,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result = Cache.convert_utc_to_local_time(
        FlightAggregates, FlightAggregates.sample_entry_date_utc.name, 'local').collect()
    assert result.select(pl.col('local')).item() == (
        sample_time.astimezone(pytz.timezone(s.skyviz.time_zone)))


def test_filter_aggregates_by_recent_days(sqlite_repo: SqliteInterface):
    '''
    Test that the filter_aggregates_by_num_days function returns
    the correct rows of the flight_aggregates table.
    '''
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    rows = [
        FlightAggregates(
            sample_entry_date_utc=now,
            number_of_flights=10,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 6, 10),
            number_of_flights=20,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result = Cache.filter_flight_aggregates_by_recent_days(1)
    assert result.select(pl.count()).item() == 1
    assert result.select(pl.col(FlightAggregates.number_of_flights.name)).item() == 10


def test_get_flight_count_last_sample():
    '''
    Test that the _get_flight_count_last_sample function returns the row
    with the most recent entry date in the flight_aggregates lazyframe
    with the number_of_flights column.
    '''
    flight_aggregates = pl.LazyFrame({
        FlightAggregates.sample_entry_date_utc.name: [datetime(2022, 5, 10),datetime(2022, 6, 10)],
        FlightAggregates.number_of_flights.name: [10, 20]
    })
    result = Cache._get_flight_count_last_sample(flight_aggregates).collect()
    assert result.select(pl.col(FlightAggregates.sample_entry_date_utc.name)).item() == (
        datetime(2022, 6, 10))
    assert result.select(pl.col(FlightAggregates.number_of_flights.name)).item() == 20
    assert result.select(pl.count()).item() == 1


def test_get_last_flight_aggregate(sqlite_repo: SqliteInterface):
    '''
    Test that the get_last_flight_aggregate function returns the most recent row
    in the flight_aggregates table.
    '''
    rows = [
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 5, 10),
            number_of_flights=10,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 6, 10),
            number_of_flights=20,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result = Cache.get_last_flight_aggregate()
    assert result.select(pl.col(FlightAggregates.sample_entry_date_utc.name)).item() == (
        datetime(2022, 6, 10))
    assert result.select(pl.col(FlightAggregates.number_of_flights.name)).item() == 20
    assert result.select(pl.count()).item() == 1


def test_get_current_flights_count(sqlite_repo: SqliteInterface):
    '''
    Test that the get_current_flights_count function returns the number of flights
    from the most recent sample in the flight_aggregates table.
    '''
    rows = [
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 5, 10),
            number_of_flights=5,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 6, 10),
            number_of_flights=20,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result = Cache.get_current_flights_count()
    assert result == 20


def test_calc_change_in_flights(sqlite_repo: SqliteInterface):
    '''
    Test that the calc_change_in_flights function returns the difference in flights
    between the most recent sample and the previous sample in the flight_aggregates table.
    '''
    rows = [
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 5, 10),
            number_of_flights=5,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
        FlightAggregates(
            sample_entry_date_utc=datetime(2022, 6, 10),
            number_of_flights=20,
            avg_ground_speed_knots=35,
            min_ground_speed_knots=30,
            max_ground_speed_knots=40,
            avg_altitude_ft=15000,
            max_altitude_ft=20000,
            max_climb_rate_ft_per_min=1000,
            max_descent_rate_ft_per_min=500,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)
    result = Cache.calc_change_in_flights()
    assert result == 15
