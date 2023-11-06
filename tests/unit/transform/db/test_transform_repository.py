from config.settings import s
from transform.db.repository import DbRepo
from database.models import FlightSamples, FlightAggregates

from sqlalchemy.orm import Session

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
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
    db = DbRepo()
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


def test_get_new_flight_samples(sqlite_repo: DbRepo):
    '''
    Test that the get_new_flight_samples method returns flight sample dates
    that have no match in the flight_aggregates table in order from most recent to oldest.
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
        FlightSamples(
            icao_id='abc789',
            sample_entry_date_utc=datetime(2023, 6, 15),
            latitude=-3.3,
            longitude=-4.4,
        ),
    ]
    aggregate_rows = [
        FlightAggregates(
            sample_entry_date_utc=datetime(2023, 6, 11),
            number_of_flights=1,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(sample_rows)
        session.add_all(aggregate_rows)
    with Session(sqlite_repo.engine) as session:
        result: Iterator[FlightSamples] = sqlite_repo.get_new_flight_samples(session)
    unmatched_sample_dates = list(result)
    assert len(unmatched_sample_dates) == 2
    assert unmatched_sample_dates[0].sample_entry_date_utc == datetime(2023, 6, 15)


@pytest.mark.skip
def test_filter_table_by_dates(sqlite_repo: DbRepo):
    assert False


@pytest.mark.skip
def test_filter_table_to_single_date(sqlite_repo: DbRepo):
    assert False


@pytest.mark.skip
def test_avg_count_aircraft_type_per_sample(sqlite_repo: DbRepo):
    assert False


@pytest.mark.skip
def test_count_num_flights_by_aircraft_type(sqlite_repo: DbRepo):
    assert False


@pytest.mark.skip
def test_count_unique_aircraft_by_aircraft_type(sqlite_repo: DbRepo):
    assert False


@pytest.mark.skip
def test_count_flights_per_month(sqlite_repo: DbRepo):
    assert False
