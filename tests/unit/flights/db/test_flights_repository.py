from flights.db.repository import DbRepo
from database.models import FlightSamples
from config.settings import s

from sqlalchemy import text
from sqlalchemy.orm import Session

import os
import pytest
from datetime import datetime


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


def test_insert_rows(sqlite_repo: DbRepo):
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


def test_insert_rows_empty_list(sqlite_repo: DbRepo):
    '''
    Tests that the insert_rows method does not raise an error when an empty list is passed in.
    '''
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, [])
