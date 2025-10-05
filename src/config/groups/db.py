from omegaconf import MISSING

from dataclasses import dataclass
import os


@dataclass
class Db:
    _target_: str = MISSING
    alembic_ini_path: str = '${project_root}/src/database/alembic.ini'
    alembic_folder_path: str = '${project_root}/src/database/alembic'


@dataclass
class PostgresProd(Db):
    _target_: str = 'database.interface.PostgresInterface'
    driver: str = 'postgresql+psycopg'
    server_name: str = 'flights-db-server'
    host: str = f'{server_name}.postgres.database.azure.com'
    port: int = 5432
    database: str = 'postgres'
    username_env_var: str = 'POSTGRES_USERNAME'
    username: str = os.environ.get(username_env_var, '')
    password_env_var: str = 'POSTGRES_PASSWORD'
    password: str = os.environ.get(password_env_var, '')


@dataclass
class PostgresStaging(Db):
    _target_: str = 'database.interface.PostgresInterface'
    driver: str = 'postgresql+psycopg'
    server_name: str = 'flights-db-server-staging'
    host: str = f'{server_name}.postgres.database.azure.com'
    port: int = 5432
    database: str = 'postgres'
    username_env_var: str = 'POSTGRES_USERNAME'
    username: str = os.environ.get(username_env_var, '')
    password_env_var: str = 'POSTGRES_PASSWORD'
    password: str = os.environ.get(password_env_var, '')


@dataclass
class PostgresDocker(Db):
    _target_: str = 'database.interface.PostgresInterface'
    driver: str = 'postgresql+psycopg'
    host: str = 'db'
    port: int = 5432
    database: str = 'flights_db'
    username: str = 'dbuser'
    password: str = 'secret'


@dataclass
class SqliteDev(Db):
    _target_: str = 'database.interface.SqliteInterface'
    database_path: str = '${project_root}/src/database/flights_db.sqlite3'


@dataclass
class SqliteTest(Db):
    _target_: str = 'database.interface.SqliteInterface'
    database_path: str = '${project_root}/src/database/test_db.sqlite3'
