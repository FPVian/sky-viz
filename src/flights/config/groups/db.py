from dataclasses import dataclass
import os


@dataclass
class Db:
    alembic_ini_path: str = '${general.project_root}/src/flights/db/alembic.ini'
    alembic_folder_path: str = '${general.project_root}/src/flights/db/alembic'


@dataclass
class PostgresProd(Db):
    _target_: str = 'flights.db.repos.postgres.PostgresRepository'
    driver: str = 'postgresql+psycopg'
    host: str = 'flights-db-server-1.postgres.database.azure.com'
    port: int = 5432
    database: str = 'postgres'
    username: str = os.environ.get('POSTGRES_PROD_ADMIN_USERNAME', '')
    password: str = os.environ.get('POSTGRES_PROD_ADMIN_PASSWORD', '')


@dataclass
class PostgresDocker(Db):
    _target_: str = 'flights.db.repos.postgres.PostgresRepository'
    driver: str = 'postgresql+psycopg'
    host: str = 'db'
    port: int = 5432
    database: str = 'flights_db'
    username: str = 'dbuser'
    password: str = 'secret'


@dataclass
class SqliteDev(Db):
    _target_: str = 'flights.db.repos.sqlite.SqliteRepository'
    database_path: str = '${general.project_root}/src/database/flights_db.sqlite3'


@dataclass
class SqliteTest(Db):
    _target_: str = 'flights.db.repos.sqlite.SqliteRepository'
    database_path: str = '${general.project_root}/src/database/test_db.sqlite3'
