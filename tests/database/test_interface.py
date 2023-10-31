from database.interface import SqliteInterface
from config.settings import s

from sqlalchemy import text
from sqlalchemy.orm import Session
from hydra.utils import instantiate

import os
import pytest


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


def test_upgrade_db(sqlite_repo: SqliteInterface):
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
