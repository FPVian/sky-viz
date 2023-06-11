from flights.config.settings import s

import os


def pytest_sessionfinish():
    try:
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
