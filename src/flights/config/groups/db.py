from flights.config.groups.secrets import PostgresSecrets

from omegaconf import MISSING

from dataclasses import dataclass


@dataclass
class Db:
    driver: str = MISSING


@dataclass
class Postgres(Db):
    driver: str = 'postgres'
    host: str = 'localhost'
    port: int = 5432
    name: str = 'flights_db'
    username: str = 'dbuser'
    password: str = PostgresSecrets.password


@dataclass
class Sqlite(Db):
    driver: str = 'sqlite'
    sqlite_path: str = 'flights_db.sqlite3'
