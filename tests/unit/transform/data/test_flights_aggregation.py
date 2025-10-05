from config.settings import s
from transform.db.repository import DbRepo
from transform.data.flight_aggregation import FlightAggregator
from database.models import FlightSamples, FlightAggregates

from sqlalchemy import text
from sqlalchemy.orm import Session
import polars as pl

import os
import pytest
from datetime import datetime
from unittest.mock import patch


@pytest.fixture
def sqlite_repo():
    '''
    Warning! This will delete a local sqlite database file, if any.
    Make sure environment is set to 'test' in conftest.py
    '''
    try:
        os.remove(s.db.database_path)
    except FileNotFoundError:
        pass
    db = DbRepo()
    db.upgrade_db()
    yield db
    os.remove(s.db.database_path)


def test_aggregate_flight_samples(sqlite_repo: DbRepo):
    '''
    Test that the aggregate_flight_samples method summarizes all unaggregrated flight samples.
    '''
    sample_rows = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=datetime(2023, 6, 11),
            latitude=1.1,
            longitude=2.2,
        ),
    ]
    with Session(sqlite_repo.engine) as session, session.begin():
        session.add_all(sample_rows)
    FlightAggregator().aggregate_flight_samples()
    with Session(sqlite_repo.engine) as session:
        result = session.execute(text('SELECT * FROM flight_aggregates')).fetchall()
    assert len(result) == 1
    assert result[0][0] == '2023-06-11 00:00:00.000000'
    assert result[0][1] == 1


def test_summarize_flight_sample():
    '''
    Test that the summarize_flight_sample method summarizes a flight sample
    into a single row of the flight_aggregates table, without failing on ties or nulls.
    '''
    sample_date = datetime(2023, 6, 11, 5, 30)
    flight_sample = pl.LazyFrame({
        FlightSamples.sample_entry_date_utc.name: [sample_date, sample_date, sample_date],
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333'],
        FlightSamples.latitude.name: [1.1, 1.2, 1.3],
        FlightSamples.longitude.name: [2.2, 2.3, 2.4],
        FlightSamples.altitude_ft.name: [13000.2, 11000.6, None],
        FlightSamples.alt_change_ft_per_min.name: [-4, 5, None],
        FlightSamples.ground_speed_knots.name: [5.4, 10.8, 10.8],
        FlightSamples.aircraft_type.name: [None, 'B222', 'C333'],
        FlightSamples.aircraft_registration.name: ['REG111', 'REG222', 'REG333'],
    })
    result = FlightAggregator().summarize_flight_sample(flight_sample)
    assert result.sample_entry_date_utc == sample_date
    assert result.number_of_flights == 3
    assert round(result.avg_altitude_ft, 1) == 12000.4
    assert result.max_altitude_ft == 13000.2
    assert result.max_alt_aircraft_type == None
    assert result.max_climb_rate_ft_per_min == 5
    assert result.max_descent_rate_ft_per_min ==  4
    assert round(result.avg_ground_speed_knots, 1) == 9.0
    assert result.max_ground_speed_knots == 10.8


def test_summarize_flight_sample_all_null():
    '''
    Test that the summarize_flight_sample method returns None 
    in average columns when all values are null.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.sample_entry_date_utc.name: [datetime(2023, 6, 11)],
        FlightSamples.flight.name: [None],
        FlightSamples.latitude.name: [1.1],
        FlightSamples.longitude.name: [2.2],
        FlightSamples.altitude_ft.name: [None],
        FlightSamples.alt_change_ft_per_min.name: [None],
        FlightSamples.ground_speed_knots.name: [None],
        FlightSamples.aircraft_type.name: [None],
        FlightSamples.aircraft_registration.name: [None],
    })
    result = FlightAggregator().summarize_flight_sample(flight_sample)
    assert result.avg_altitude_ft == None
    assert result.avg_ground_speed_knots == None


def test_calculate_max_climb_rate():
    '''
    Test that the _calculate_max_climb_rate inserts the flight with the maximum climb rate
    into a row of the flight_aggregates table, without failing on nulls.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333'],
        FlightSamples.alt_change_ft_per_min.name: [-4, 5, None],
        FlightSamples.aircraft_type.name: [None, 'B222', 'C333'],
        FlightSamples.aircraft_registration.name: ['REG111', 'REG222', 'REG333'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_climb_rate(flight_sample, row)
    assert result.max_climb_rate_ft_per_min == 5
    assert result.max_climb_aircraft_type == 'B222'
    assert result.max_climb_aircraft_registration == 'REG222'
    assert result.max_climb_flight == 'FLIGHT222'


def test_calculate_max_descent_rate():
    '''
    Test that the _calculate_max_descent_rate inserts the flight with the maximum descent rate
    into a row of the flight_aggregates table, without failing on nulls.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333'],
        FlightSamples.alt_change_ft_per_min.name: [-4, 5, None],
        FlightSamples.aircraft_type.name: ['A111', 'B222', 'C333'],
        FlightSamples.aircraft_registration.name: ['REG111', 'REG222', 'REG333'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_descent_rate(flight_sample, row)
    assert result.max_descent_rate_ft_per_min ==  4
    assert result.max_descent_aircraft_type == 'A111'
    assert result.max_descent_aircraft_registration == 'REG111'
    assert result.max_descent_flight == 'FLIGHT111'


def test_calculate_max_descent_rate_skips_on_nulls():
    '''
    Test that the _calculate_max_descent_rate doesn't alter the row when all values are null.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333'],
        FlightSamples.alt_change_ft_per_min.name: [None, None, None],
        FlightSamples.aircraft_type.name: ['A111', 'B222', 'C333'],
        FlightSamples.aircraft_registration.name: ['REG111', 'REG222', 'REG333'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_descent_rate(flight_sample, row)
    assert result.max_descent_rate_ft_per_min ==  None
    assert result.max_descent_aircraft_type == None
    assert result.max_descent_aircraft_registration == None
    assert result.max_descent_flight == None


def test_calculate_max_columns():
    '''
    Test that the _calculate_max_min_columns method adds columns for the maximum values
    in a search column to the flight_aggregates row, without failing on ties or nulls.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333', 'FLIGHT444'],
        FlightSamples.ground_speed_knots.name: [5.4, 10.8, 10.8, None],
        FlightSamples.aircraft_type.name: [None, 'B222', 'C333', 'D444'],
        FlightSamples.aircraft_registration.name: ['REG111', None, 'REG333', 'REG444'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_min_columns(
        flight_sample, row, FlightSamples.ground_speed_knots, FlightAggregates.max_ground_speed_knots,
        FlightAggregates.max_speed_aircraft_type, FlightAggregates.max_speed_aircraft_registration,
        FlightAggregates.max_speed_flight, FlightAggregator.AggregationType.MAX)
    assert result.max_ground_speed_knots == 10.8
    assert result.max_speed_aircraft_type in ['B222', 'C333']
    assert result.max_speed_aircraft_registration in [None, 'REG333']
    assert result.max_speed_flight in ['FLIGHT222', 'FLIGHT333']


def test_calculate_min_columns():
    '''
    Test that the _calculate_max_min_columns method adds columns for the minimum values
    in a search column to the flight_aggregates row, without failing on nulls.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111', 'FLIGHT222', 'FLIGHT333'],
        FlightSamples.alt_change_ft_per_min.name: [-4, 5, None],
        FlightSamples.aircraft_type.name: [None, 'B222', 'C333'],
        FlightSamples.aircraft_registration.name: ['REG111', 'REG222', 'REG333'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_min_columns(
        flight_sample, row, FlightSamples.alt_change_ft_per_min,
        FlightAggregates.max_descent_rate_ft_per_min, FlightAggregates.max_descent_aircraft_type,
        FlightAggregates.max_descent_aircraft_registration, FlightAggregates.max_descent_flight,
        FlightAggregator.AggregationType.MIN)
    assert result.max_descent_rate_ft_per_min ==  -4
    assert result.max_descent_aircraft_type == None
    assert result.max_descent_aircraft_registration == 'REG111'
    assert result.max_descent_flight == 'FLIGHT111'


@patch('transform.data.flight_aggregation.log')
def test_calculate_max_min_columns_all_null(mock_log):
    '''
    Test that the _calculate_max_min_columns method only logs a warning when all search values are null.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.flight.name: ['FLIGHT111'],
        FlightSamples.ground_speed_knots.name: [None],
        FlightSamples.aircraft_type.name: ['B222'],
        FlightSamples.aircraft_registration.name: ['REG111'],
    })
    row = FlightAggregates()
    result = FlightAggregator()._calculate_max_min_columns(
        flight_sample, row, FlightSamples.ground_speed_knots, FlightAggregates.max_ground_speed_knots,
        FlightAggregates.max_speed_aircraft_type, FlightAggregates.max_speed_aircraft_registration,
        FlightAggregates.max_speed_flight, FlightAggregator.AggregationType.MAX)
    assert mock_log.warning.call_count == 1
    assert result.max_speed_aircraft_registration == None