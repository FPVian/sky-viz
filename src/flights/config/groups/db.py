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
    server_name: str = 'flights-db-server'
    host: str = f'{server_name}.postgres.database.azure.com'
    port: int = 5432
    database: str = 'postgres'
    username_env_var: str = 'POSTGRES_PROD_USERNAME'
    username: str = os.environ.get(username_env_var, '')
    password_env_var: str = 'POSTGRES_PROD_PASSWORD'
    password: str = os.environ.get(password_env_var, '')
    admin_username: str = os.environ.get('POSTGRES_PROD_ADMIN_USERNAME', '')
    admin_password: str = os.environ.get('POSTGRES_PROD_ADMIN_PASSWORD', '')


@dataclass
class PostgresStaging(Db):
    _target_: str = 'flights.db.repos.postgres.PostgresRepository'
    driver: str = 'postgresql+psycopg'
    server_name: str = 'flights-db-server-staging'
    host: str = f'{server_name}.postgres.database.azure.com'
    port: int = 5432
    database: str = 'postgres'
    username_env_var: str = 'POSTGRES_STAGING_USERNAME'
    username: str = os.environ.get(username_env_var, '')
    password_env_var: str = 'POSTGRES_STAGING_PASSWORD'
    password: str = os.environ.get(password_env_var, '')
    admin_username: str = os.environ.get('POSTGRES_STAGING_ADMIN_USERNAME', '')
    admin_password: str = os.environ.get('POSTGRES_STAGING_ADMIN_PASSWORD', '')


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
