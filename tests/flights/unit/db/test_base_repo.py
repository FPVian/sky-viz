from flights.db.repos.sqlite import SqliteRepository
from database.models import FlightSamples, FlightAggregates
from flights.config.settings import s

from sqlalchemy import text
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
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
    db: SqliteRepository = instantiate(s.db)
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


def test_insert_rows(sqlite_repo: SqliteRepository):
    '''
    Test that the insert_rows method inserts rows into the database.
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
        sqlite_repo.insert_rows(session, iter(rows))
    with Session(sqlite_repo.engine) as session:
        result = session.execute(text('SELECT * FROM flight_samples')).fetchall()
    assert 'abc123' in result[0]
    assert 'abc456' in result[1]


def test_insert_rows_empty_list(sqlite_repo: SqliteRepository):
    '''
    Tests that the insert_rows method does not raise an error when an empty list is passed in.
    '''
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, [])


def test_upgrade_db(sqlite_repo: SqliteRepository):
    '''
    Tests that the upgrade_db method upgrades the database to the latest version.
    '''
    with Session(sqlite_repo.engine) as session:
        tables_result = session.execute(text("""PRAGMA table_list;""")).fetchall()
        columns_result = session.execute(text("""PRAGMA table_info(flight_samples);""")).fetchall()

    table_names = [table[1] for table in tables_result]
    assert 'flight_samples' in table_names
    column_names = [column[1] for column in columns_result]
    assert 'sample_entry_date_utc' in column_names


def test_get_new_flight_samples(sqlite_repo: SqliteRepository):
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
    with Session(sqlite_repo.engine) as session:
        result: Iterator[FlightSamples] = sqlite_repo.get_new_flight_samples(session)
    unmatched_sample_dates = list(result)
    assert len(unmatched_sample_dates) == 1
    assert unmatched_sample_dates[0].sample_entry_date_utc == datetime(2023, 6, 10)


def test_count_flight_samples_by_date(sqlite_repo: SqliteRepository):
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
    with Session(sqlite_repo.engine) as session:
        results: list[int] = [
            sqlite_repo.count_flight_samples_by_date(session, datetime(2023, 6, 10)),
            sqlite_repo.count_flight_samples_by_date(session, datetime(2023, 6, 11)),
            sqlite_repo.count_flight_samples_by_date(session, datetime(2023, 6, 12)),
        ]
    assert results[0] == 0
    assert results[1] == 2
    assert results[2] == 1