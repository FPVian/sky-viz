from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime
from typing import Optional

'''
See the docs for SQLAlchemy annotated declarative tables here:
https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column
'''


class Base(DeclarativeBase):
    __tablename__: str


class FlightSamples(Base):
    __tablename__ = 'flight_samples'
    icao_id: Mapped[str] = mapped_column(primary_key=True)
    sample_entry_date_utc: Mapped[datetime] = mapped_column(primary_key=True)
    flight: Mapped[Optional[str]]
    latitude: Mapped[float]
    longitude: Mapped[float]
    altitude_ft: Mapped[Optional[int]]
    alt_change_ft_per_min: Mapped[Optional[int]]
    heading: Mapped[Optional[float]]
    ground_speed_knots: Mapped[Optional[float]]
    nav_modes: Mapped[Optional[str]]
    emitter_category: Mapped[Optional[str]]
    aircraft_type: Mapped[Optional[str]]
    aircraft_registration: Mapped[Optional[str]]
    flag: Mapped[Optional[str]]
    source: Mapped[Optional[str]]
    rssi: Mapped[Optional[float]]
    emergency: Mapped[Optional[str]]


class FlightAggregates (Base):
    __tablename__ = 'flight_aggregates'
    sample_entry_date_utc: Mapped[datetime] = mapped_column(primary_key=True)
    number_of_flights: Mapped[int]
