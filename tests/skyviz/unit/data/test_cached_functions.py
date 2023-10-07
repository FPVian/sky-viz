from flights.db.repos.sqlite import SqliteRepository
from flights.config.settings import s
from database.models import FlightSamples
from skyviz.data.cached_functions import read_table

from hydra.utils import instantiate
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
    db: SqliteRepository = instantiate(s.db)
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


def test_read_table(sqlite_repo: SqliteRepository):
    '''
    Test that the read_table function reads rows from the database into a pandas dataframe.
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
    result = read_table(FlightSamples)
    result_dict = result.to_dict()
    assert result_dict['icao_id'] == {0: 'abc123', 1: 'abc456'}
