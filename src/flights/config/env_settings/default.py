from flights.config.env_settings import secrets

from pathlib import Path

'''
Settings usually must exist in Defaults to work with code completion
'''


class Settings(secrets.Default):
    ENV_VAR_NAME: str = 'FLIGHTS_ENV'
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    PROJECT_ROOT: Path = BASE_DIR.parent.parent

    class Logs():
        LEVEL: str = 'INFO'
        LOG_TO_CONSOLE: bool = True
        PATH: Path = Path(__file__).resolve().parent.parent.parent.parent.parent
        NAME: str = 'flights.log'
        FILE_PATH: str = f'{PATH}/{NAME}'
        STREAM_FORMAT: str = '[%(levelname)s] %(module)-12s - %(message)s'
        FILE_FORMAT: str = '[%(levelname)s] %(asctime)s %(name)-40s: %(funcName)-15s - %(message)-50s (pid:%(process)s)'
        BYTES_PER_FILE: int = 1000000  # must be nonzero to rotate
        NUMBER_OF_BACKUPS: int = 1  # must be nonzero to rotate

    class Database(secrets.Default.Database):
        DRIVER: str = 'sqlite'  # 'sqlite' or 'postgres'
        SQLITE_PATH: str = 'db.sqlite3'

        class Postgres(secrets.Default.Database.Postgres):
            HOST: str = 'localhost'
            PORT: int = 5432
            DB_NAME: str = 'flights_db'
            USERNAME: str = 'dbuser'

    class Api:
        TIMEOUT: int = 5
        NUMBER_OF_TRIES: int = 5
