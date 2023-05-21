from flights.config.env_settings import secrets

from pathlib import Path

'''
Settings usually must exist in Defaults to work with code completion
'''


class Settings(secrets.Default):
    ENV_VAR_NAME = 'FLIGHTS_ENV'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    PROJECT_ROOT = BASE_DIR.parent.parent

    class Logs():
        LEVEL = 'INFO'
        LOG_TO_CONSOLE = True
        PATH = Path(__file__).resolve().parent.parent.parent.parent.parent
        NAME = 'flights.log'
        FILE_PATH = f'{PATH}/{NAME}'
        STREAM_FORMAT = '[%(levelname)s] %(module)-12s - %(message)s'
        FILE_FORMAT = '[%(levelname)s] %(asctime)s %(name)-40s: %(funcName)-15s - %(message)-50s (pid:%(process)s)'
        BYTES_PER_FILE = 1000000  # must be nonzero to rotate
        NUMBER_OF_BACKUPS = 1  # must be nonzero to rotate

    class Database:
        DRIVER = 'sqlite'
        SQLITE_PATH = 'db.sqlite3'
        POSTGRES_URL = 'pass'
