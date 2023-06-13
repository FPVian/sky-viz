from flights.db.repos.sqlite import SqliteRepository
from database.models import FlightSamples
from flights.config.settings import s

from sqlalchemy import text
from sqlalchemy.orm import Session
from hydra.utils import instantiate

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
    sqlite_repo.insert_rows(rows)
    with Session(sqlite_repo.engine) as session:
        result = session.execute(text('SELECT * FROM flight_samples')).fetchall()
    assert 'abc123' in result[0]
    assert 'abc456' in result[1]


def test_insert_rows_empty_list(sqlite_repo: SqliteRepository):
    '''
    Tests that the insert_rows method does not raise an error when an empty list is passed in.
    '''
    sqlite_repo.insert_rows([])


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
