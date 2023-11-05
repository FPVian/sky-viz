from config.settings import s
from transform.db.repository import DbRepo
from transform.data.aggregation import FlightsProcessor
from database.models import FlightSamples

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
    FlightsProcessor().aggregate_flight_samples()
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
        FlightSamples.icao_id.name: ['aaa111', 'bbb222', 'ccc333'],
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
    result = FlightsProcessor().summarize_flight_sample(flight_sample)
    assert result.sample_entry_date_utc == sample_date
    assert result.number_of_flights == 3
    assert round(result.avg_altitude_ft, 1) == 12000.4
    assert result.max_altitude_ft == 13000.2
    assert result.max_alt_aircraft_type == None
    assert result.max_alt_aircraft_registration == 'REG111'
    assert result.max_alt_flight == 'FLIGHT111'
    assert result.max_climb_rate_ft_per_min == 5
    assert result.max_climb_aircraft_type == 'B222'
    assert result.max_climb_aircraft_registration == 'REG222'
    assert result.max_climb_flight == 'FLIGHT222'
    assert result.max_descent_rate_ft_per_min ==  4
    assert result.max_descent_aircraft_type == None
    assert result.max_descent_aircraft_registration == 'REG111'
    assert result.max_descent_flight == 'FLIGHT111'
    assert round(result.avg_ground_speed_knots, 1) == 9.0
    assert result.max_ground_speed_knots == 10.8
    assert result.max_speed_aircraft_type == 'B222'
    assert result.max_speed_aircraft_registration == 'REG222'
    assert result.max_speed_flight == 'FLIGHT222'

@patch('transform.data.aggregation.log')
def test_summarize_flight_sample_all_null(mock_log):
    '''
    Test that the summarize_flight_sample method logs warnings when all values are null.
    '''
    flight_sample = pl.LazyFrame({
        FlightSamples.icao_id.name: ['aaa111'],
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
    result = FlightsProcessor().summarize_flight_sample(flight_sample)
    assert result.number_of_flights == 1
    assert result.avg_altitude_ft == None
    assert result.max_altitude_ft == None
    assert result.max_climb_rate_ft_per_min == None
    assert result.max_descent_rate_ft_per_min ==  None
    assert result.max_ground_speed_knots == None
    assert mock_log.warning.call_count == 4


def test_filter_to_max_row():
    '''
    Test that the _filter_to_max_row method filters a dataframe to a single row
    matching the max value in a specified column, without failing on ties or nulls.
    '''
    sample_date = datetime(2023, 6, 11, 5, 30)
    flight_sample = pl.LazyFrame({
        FlightSamples.icao_id.name: ['aaa111', 'bbb222', 'ccc333', 'ddd444'],
        FlightSamples.sample_entry_date_utc.name: [sample_date, sample_date, sample_date, sample_date],
        FlightSamples.latitude.name: [5.1, 5.1, 1.3, 3.3],
        FlightSamples.longitude.name: [2.2, 2.3, 2.4, 2.3],
        FlightSamples.altitude_ft.name: [13000.2, 13000.2, 11000, None],
    })
    result = FlightsProcessor()._filter_to_max_row(flight_sample, FlightSamples.altitude_ft)
    assert result[FlightSamples.icao_id.name].item() in ['aaa111', 'bbb222']


def test_filter_to_min_row():
    '''
    Test that the _filter_to_max_row method filters a dataframe to a single row
    matching the max value in a specified column, without failing on ties or nulls.
    '''
    sample_date = datetime(2023, 6, 11, 5, 30)
    flight_sample = pl.LazyFrame({
        FlightSamples.icao_id.name: ['aaa111', 'bbb222', 'ccc333', 'ddd444'],
        FlightSamples.sample_entry_date_utc.name: [sample_date, sample_date, sample_date, sample_date],
        FlightSamples.latitude.name: [5.1, 5.1, 1.3, 3.3],
        FlightSamples.longitude.name: [2.2, 2.3, 2.4, 2.3],
        FlightSamples.altitude_ft.name: [13000.2, 11000, 11000, None],
    })
    result = FlightsProcessor()._filter_to_min_row(flight_sample, FlightSamples.altitude_ft)
    assert result[FlightSamples.icao_id.name].item() in ['ccc333', 'bbb222']
