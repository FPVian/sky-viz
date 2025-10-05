from database.interface import SqliteInterface
from skyviz.db.repository import DbRepo
from database.models import FlightSamples
from config.settings import s

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
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
    db: SqliteInterface = instantiate(s.db)
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


@patch('skyviz.db.repository.datetime')
def test_calc_minutes_since_last_update(mock_dt, sqlite_repo: SqliteInterface):
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
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)

    db = DbRepo()
    with Session(db.engine) as session, session.begin():
        result = db.calc_minutes_since_last_update(session, FlightSamples.sample_entry_date_utc)
    assert result == 10


def test_count_total_rows(sqlite_repo: SqliteInterface):
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
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)

    db = DbRepo()
    with Session(db.engine) as session, session.begin():
        result = db.count_total_rows(session, FlightSamples)
    assert result == 2


def test_count_distinct(sqlite_repo: SqliteInterface):
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
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(rows)

    db = DbRepo()
    with Session(db.engine) as session, session.begin():
        result = db.count_distinct(session, FlightSamples.sample_entry_date_utc)
    assert result == 2
