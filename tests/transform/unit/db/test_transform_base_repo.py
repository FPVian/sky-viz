from flights.config.settings import s as flights_s
from flights.db.repos.sqlite import SqliteRepository as FlightsDbRepo
from transform.config.settings import s
from transform.db.repos.sqlite import SqliteRepository
from database.models import FlightSamples, FlightAggregates

from sqlalchemy.orm import Session
from hydra.utils import instantiate

import os
import pytest
from datetime import datetime
from typing import Iterator


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
    db: FlightsDbRepo = instantiate(flights_s.db)
    db.upgrade_db()
    yield db
    os.remove(flights_s.db.database_path)


def test_get_new_flight_samples(sqlite_repo: FlightsDbRepo):
    '''
    Test that the get_new_flight_samples method returns flight sample dates
    that have no match in the flight_aggregates table.
    '''
    sample_rows = [
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
    aggregate_rows = [
        FlightAggregates(
            sample_entry_date_utc=datetime(2023, 6, 11),
            number_of_flights=1,
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
        sqlite_repo.insert_rows(session, iter(sample_rows))
        sqlite_repo.insert_rows(session, iter(aggregate_rows))
    db: SqliteRepository = instantiate(s.db)
    with Session(db.engine) as session:
        result: Iterator[FlightSamples] = db.get_new_flight_samples(session)
    unmatched_sample_dates = list(result)
    assert len(unmatched_sample_dates) == 1
    assert unmatched_sample_dates[0].sample_entry_date_utc == datetime(2023, 6, 10)


def test_count_flight_samples_by_date(sqlite_repo: FlightsDbRepo):
    '''
    Test that the count_flight_samples_by_date method 
    returns the number of flight samples for a given date.
    '''
    sample_rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=1.1,
            longitude=2.2,
        ),
        FlightSamples(
            icao_id='abc456',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=-3.3,
            longitude=-4.4,
        ),
        FlightSamples(
            icao_id='abc789',
            sample_entry_date_utc=datetime(2023, 6, 12),
            latitude=-5.5,
            longitude=-6.6,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, iter(sample_rows))
    db: SqliteRepository = instantiate(s.db)
    with Session(db.engine) as session:
        results: list[int] = [
            db.count_flight_samples_by_date(session, datetime(2023, 6, 10)),
            db.count_flight_samples_by_date(session, datetime(2023, 6, 11)),
            db.count_flight_samples_by_date(session, datetime(2023, 6, 12)),
        ]
    assert results[0] == 0
    assert results[1] == 2
    assert results[2] == 1


def test_filter_table_by_dates(sqlite_repo: FlightsDbRepo):
    assert False


def test_filter_table_to_single_date(sqlite_repo: FlightsDbRepo):
    assert False


def test_avg_count_aircraft_type_per_sample(sqlite_repo: FlightsDbRepo):
    assert False


def test_count_num_flights_by_aircraft_type(sqlite_repo: FlightsDbRepo):
    assert False


def test_count_unique_aircraft_by_aircraft_type(sqlite_repo: FlightsDbRepo):
    assert False


def test_count_flights_per_month(sqlite_repo: FlightsDbRepo):
    assert False
