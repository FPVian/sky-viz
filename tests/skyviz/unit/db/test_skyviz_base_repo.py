from flights.db.repos.sqlite import SqliteRepository as FlightsDbRepo
from skyviz.db.repos.sqlite import SqliteRepository
from database.models import FlightSamples
from flights.config.settings import s as flights_s
from skyviz.config.settings import s

from hydra.utils import instantiate
from sqlalchemy.orm import Session

import os
import pytest
from datetime import datetime
from unittest.mock import patch


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


@patch('skyviz.db.base_repo.datetime')
def test_calc_minutes_since_last_update(mock_dt, sqlite_repo: FlightsDbRepo):
    '''
    Test that the calc_minutes_since_last_update method correctly calculates a time difference
    between now and the most recent row.
    '''
    mock_dt.utcnow.return_value = datetime(2023, 6, 11, 13, 43)
    latest_row_date = datetime(2023, 6, 11, 13, 33)

    rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 10),
            latitude=1.1,
            longitude=2.2,
        ),
        FlightSamples(
            icao_id='abc456',
            sample_entry_date_utc=latest_row_date,
            latitude=-3.3,
            longitude=-4.4,
        ),
    ]
    sqlite_repo.insert_rows(iter(rows))

    db: SqliteRepository = instantiate(s.db)
    with Session(db.engine) as session, session.begin():
        result = db.calc_minutes_since_last_update(session, FlightSamples.sample_entry_date_utc)
    assert result == 10


def test_count_total_rows(sqlite_repo: FlightsDbRepo):
    '''
    Test that the count_total_rows method correctly counts the total number of rows in the table.
    '''
    rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 10),
            latitude=1.1,
            longitude=2.2,
        ),
        FlightSamples(
            icao_id='abc456',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=-3.3,
            longitude=-4.4,
        ),
    ]
    sqlite_repo.insert_rows(iter(rows))

    db: SqliteRepository = instantiate(s.db)
    with Session(db.engine) as session, session.begin():
        result = db.count_total_rows(session, FlightSamples)
    assert result == 2


def test_count_distinct(sqlite_repo: FlightsDbRepo):
    '''
    Test that the count_total_rows method counts the number of unique dates in sample_entry_date_utc.
    '''
    rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 10),
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
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=-5.5,
            longitude=-6.6,
        ),
    ]
    sqlite_repo.insert_rows(iter(rows))

    db: SqliteRepository = instantiate(s.db)
    with Session(db.engine) as session, session.begin():
        result = db.count_distinct(session, FlightSamples.sample_entry_date_utc)
    assert result == 2
