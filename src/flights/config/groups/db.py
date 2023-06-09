from flights.config.groups.secrets import PostgresSecrets

from dataclasses import dataclass


@dataclass
class Db:
    alembic_ini_path: str = '${general.project_root}/src/flights/db/alembic.ini'
    alembic_folder_path: str = '${general.project_root}/src/flights/db/alembic'


@dataclass
class PostgresDocker(Db):
    _target_: str = 'flights.db.repos.postgres.PostgresRepository'
    driver: str = 'postgresql+psycopg'
    host: str = 'localhost'
    port: int = 5432
    database: str = 'flights_db'
    username: str = 'dbuser'
    password: str = PostgresSecrets.password


@dataclass
class Sqlite(Db):
    _target_: str = 'flights.db.repos.sqlite.SqliteRepository'
    database_path: str = '${general.project_root}/src/flights/db/flights_db.sqlite3'
