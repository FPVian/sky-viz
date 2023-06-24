from skyviz.config.groups.secrets import PostgresSecrets

from dataclasses import dataclass


@dataclass
class Db:
    pass


@dataclass
class PostgresDocker(Db):
    _target_: str = 'skyviz.db.repos.postgres.PostgresRepository'
    driver: str = 'postgresql+psycopg'
    host: str = 'db'
    port: int = 5432
    database: str = 'flights_db'
    username: str = 'dbuser'
    password: str = PostgresSecrets.password


@dataclass
class SqliteDev(Db):
    _target_: str = 'skyviz.db.repos.sqlite.SqliteRepository'
    database_path: str = '${general.project_root}/src/database/flights_db.sqlite3'


@dataclass
class SqliteTest(Db):
    _target_: str = 'skyviz.db.repos.sqlite.SqliteRepository'
    database_path: str = '${general.project_root}/src/database/test_db.sqlite3'
