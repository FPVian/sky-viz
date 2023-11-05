from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime, date 
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


class RecentFlightSamples(Base):
    __tablename__ = 'recent_flight_samples'
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


class RandomFlightSamples(Base):
    __tablename__ = 'random_flight_samples'
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


class FlightEmergencies(Base):
    __tablename__ = 'flight_emergencies'
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


class FlightAggregates(Base):
    __tablename__ = 'flight_aggregates'
    sample_entry_date_utc: Mapped[datetime] = mapped_column(primary_key=True)
    number_of_flights: Mapped[int]
    avg_altitude_ft: Mapped[Optional[float]]
    max_altitude_ft: Mapped[Optional[int]]
    max_alt_aircraft_type: Mapped[Optional[str]]
    max_alt_aircraft_registration: Mapped[Optional[str]]
    max_alt_flight: Mapped[Optional[str]]
    max_climb_rate_ft_per_min: Mapped[Optional[int]]
    max_climb_aircraft_type: Mapped[Optional[str]]
    max_climb_aircraft_registration: Mapped[Optional[str]]
    max_climb_flight: Mapped[Optional[str]]
    max_descent_rate_ft_per_min: Mapped[Optional[int]]
    max_descent_aircraft_type: Mapped[Optional[str]]
    max_descent_aircraft_registration: Mapped[Optional[str]]
    max_descent_flight: Mapped[Optional[str]]
    avg_ground_speed_knots: Mapped[Optional[float]]
    max_ground_speed_knots: Mapped[Optional[float]]
    max_speed_aircraft_type: Mapped[Optional[str]]
    max_speed_aircraft_registration: Mapped[Optional[str]]
    max_speed_flight: Mapped[Optional[str]]


class DailyFlightTotals(Base):
    __tablename__ = 'daily_flight_aggregates'
    sample_date: Mapped[date] = mapped_column(primary_key=True)
    day_of_week: Mapped[str]  # 'Tue'
    day_and_number: Mapped[str]  # 'Mon 23'
    sample_size: Mapped[int]
    total_unique_flights: Mapped[int]
    max_aircraft: Mapped[int]
    avg_aircraft: Mapped[float]
    min_aircraft: Mapped[int]
    avg_altitude_ft: Mapped[Optional[float]]
    max_altitude_ft: Mapped[Optional[int]]
    max_alt_aircraft_type: Mapped[Optional[str]]
    max_alt_aircraft_registration: Mapped[Optional[str]]
    max_alt_flight: Mapped[Optional[str]]
    max_climb_rate_ft_per_min: Mapped[Optional[int]]
    max_climb_aircraft_type: Mapped[Optional[str]]
    max_climb_aircraft_registration: Mapped[Optional[str]]
    max_climb_flight: Mapped[Optional[str]]
    max_descent_rate_ft_per_min: Mapped[Optional[int]]
    max_descent_aircraft_type: Mapped[Optional[str]]
    max_descent_aircraft_registration: Mapped[Optional[str]]
    max_descent_flight: Mapped[Optional[str]]
    avg_ground_speed_knots: Mapped[Optional[float]]
    max_ground_speed_knots: Mapped[Optional[float]]
    max_speed_aircraft_type: Mapped[Optional[str]]
    max_speed_aircraft_registration: Mapped[Optional[str]]
    max_speed_flight: Mapped[Optional[str]]


class WeeklyFlightTotals(Base):
    __tablename__ = 'weekly_flight_aggregates'
    week_start_date: Mapped[date] = mapped_column(primary_key=True)
    week_of_year: Mapped[int]
    sample_size: Mapped[int]
    total_unique_flights: Mapped[int]
    max_aircraft: Mapped[int]
    avg_aircraft: Mapped[float]
    min_aircraft: Mapped[int]
    avg_altitude_ft: Mapped[Optional[float]]
    max_altitude_ft: Mapped[Optional[int]]
    max_alt_aircraft_type: Mapped[Optional[str]]
    max_alt_aircraft_registration: Mapped[Optional[str]]
    max_alt_flight: Mapped[Optional[str]]
    max_climb_rate_ft_per_min: Mapped[Optional[int]]
    max_climb_aircraft_type: Mapped[Optional[str]]
    max_climb_aircraft_registration: Mapped[Optional[str]]
    max_climb_flight: Mapped[Optional[str]]
    max_descent_rate_ft_per_min: Mapped[Optional[int]]
    max_descent_aircraft_type: Mapped[Optional[str]]
    max_descent_aircraft_registration: Mapped[Optional[str]]
    max_descent_flight: Mapped[Optional[str]]
    avg_ground_speed_knots: Mapped[Optional[float]]
    max_ground_speed_knots: Mapped[Optional[float]]
    max_speed_aircraft_type: Mapped[Optional[str]]
    max_speed_aircraft_registration: Mapped[Optional[str]]
    max_speed_flight: Mapped[Optional[str]]


class MonthlyFlightTotals(Base):
    __tablename__ = 'monthly_flight_aggregates'
    month_start_date: Mapped[date] = mapped_column(primary_key=True)
    month: Mapped[str]  # 'Jan'
    month_and_year: Mapped[str]  # 'Mar 21'
    short_month_year: Mapped[str]  # '3/21'
    sample_size: Mapped[int]
    total_unique_flights: Mapped[int]
    max_aircraft: Mapped[int]
    avg_aircraft: Mapped[float]
    min_aircraft: Mapped[int]
    avg_altitude_ft: Mapped[Optional[float]]
    max_altitude_ft: Mapped[Optional[int]]
    max_alt_aircraft_type: Mapped[Optional[str]]
    max_alt_aircraft_registration: Mapped[Optional[str]]
    max_alt_flight: Mapped[Optional[str]]
    max_climb_rate_ft_per_min: Mapped[Optional[int]]
    max_climb_aircraft_type: Mapped[Optional[str]]
    max_climb_aircraft_registration: Mapped[Optional[str]]
    max_climb_flight: Mapped[Optional[str]]
    max_descent_rate_ft_per_min: Mapped[Optional[int]]
    max_descent_aircraft_type: Mapped[Optional[str]]
    max_descent_aircraft_registration: Mapped[Optional[str]]
    max_descent_flight: Mapped[Optional[str]]
    avg_ground_speed_knots: Mapped[Optional[float]]
    max_ground_speed_knots: Mapped[Optional[float]]
    max_speed_aircraft_type: Mapped[Optional[str]]
    max_speed_aircraft_registration: Mapped[Optional[str]]
    max_speed_flight: Mapped[Optional[str]]


class DailyTopAircraft(Base):
    __tablename__ = 'daily_top_aircraft'
    sample_date: Mapped[date] = mapped_column(primary_key=True)
    day_of_week: Mapped[str]  # 'Tue'
    day_and_number: Mapped[str]  # 'Mon 23'
    aircraft_type: Mapped[str]  = mapped_column(primary_key=True)
    num_of_samples: Mapped[int]
    num_per_sample: Mapped[float]
    usage_rank: Mapped[int]
    num_flights: Mapped[int]
    flights_rank: Mapped[int]
    num_unique_aircraft: Mapped[int]
    aircraft_rank: Mapped[int]


class WeeklyTopAircraft(Base):
    __tablename__ = 'weekly_top_aircraft'
    week_start_date: Mapped[date] = mapped_column(primary_key=True)
    week_of_year: Mapped[int]
    aircraft_type: Mapped[str]  = mapped_column(primary_key=True)
    num_of_samples: Mapped[int]
    num_per_sample: Mapped[float]
    usage_rank: Mapped[int]
    num_flights: Mapped[int]
    flights_rank: Mapped[int]
    num_unique_aircraft: Mapped[int]
    aircraft_rank: Mapped[int]


class MonthlyTopAircraft(Base):
    __tablename__ = 'monthly_top_aircraft'
    month_start_date: Mapped[date] = mapped_column(primary_key=True)
    month: Mapped[str]  # 'Jan'
    month_and_year: Mapped[str]  # 'Mar 21'
    short_month_year: Mapped[str]  # '3/21'
    aircraft_type: Mapped[str]  = mapped_column(primary_key=True)
    num_of_samples: Mapped[int]
    num_per_sample: Mapped[float]
    usage_rank: Mapped[int]
    num_flights: Mapped[int]
    flights_rank: Mapped[int]
    num_unique_aircraft: Mapped[int]
    aircraft_rank: Mapped[int]


class MonthlyTopFlights(Base):
    __tablename__ = 'monthly_top_flights'
    month_start_date: Mapped[date] = mapped_column(primary_key=True)
    month: Mapped[str]  # 'Jan'
    month_and_year: Mapped[str]  # 'Mar 21'
    short_month_year: Mapped[str]  # '3/21'
    flight: Mapped[str]  = mapped_column(primary_key=True)
    num_days_flown: Mapped[int]
    monthly_rank: Mapped[int]
