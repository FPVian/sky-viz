from flights.config.settings import s as flights_s
from transform.db.repos.sqlite import SqliteRepository
from transform.data.aggregation import FlightsProcessor
from database.models import FlightSamples

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
        os.remove(flights_s.db.database_path)
    except FileNotFoundError:
        pass
    db: SqliteRepository = instantiate(flights_s.db)
    db.upgrade_db()
    yield db
    os.remove(flights_s.db.database_path)


def test_summarize_flight_samples(sqlite_repo: SqliteRepository):
    '''
    Test that the summarize_flight_samples method summarizes flight samples.
    '''
    sample_rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=1.1,
            longitude=2.2,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        sqlite_repo.insert_rows(session, iter(sample_rows))
    with Session(sqlite_repo.engine) as session, session.begin():
        FlightsProcessor().summarize_flight_samples(session, sqlite_repo)
    with Session(sqlite_repo.engine) as session:
        result = session.execute(text('SELECT * FROM flight_aggregates')).fetchall()
    assert len(result) == 1
    assert result[0][0] == '2023-06-11 00:00:00.000000'
    assert result[0][1] == 1