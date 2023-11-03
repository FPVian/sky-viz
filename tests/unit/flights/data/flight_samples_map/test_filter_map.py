from flights.data.flight_samples_map import FlightSamplesMapper
from database.models import FlightSamples

import pytest

from unittest.mock import patch
from datetime import datetime
import pytz


@pytest.fixture
def flight_data():
    return [
        {
            'hex': 'abc123',
            'flight': '123ABC',
            'lat': '40.712776',
            'lon': '-74.005974',
            'alt_baro': 'bad data',
            'baro_rate': '300',
            'track': '120.5',
            'gs': 'bad data',
            'nav_modes': ['autopilot'],
            'category': 'A1',
            't': 'B737',
            'r': 'USA',
            'dbFlags': '1',
            'type': 'adsb',
            'rssi': '-30',
            'emergency': 'none',
            'squawk': '7700'
        },
        {
            'hex': 'def456',
            'flight': '456DEF',
            'lat': '34.052235',
            'lon': '-118.243683',
            'alt_baro': 'ground',
            'baro_rate': '400',
            'geom_rate': '500',
            'track': '230.5',
            'gs': '600',
            'nav_modes': ['manual'],
            'category': 'B1',
            't': 'A320',
            'r': 'USA',
            'dbFlags': '2',
            'type': 'mlat',
            'rssi': '-40',
            'emergency': 'emergency',
            'squawk': '7600'
        }
    ]


@patch('flights.data.flight_samples_map.datetime')
def test_map_scatter_data(mock_dt, flight_data: list[dict]):
    '''
    Test that map_scatter_data returns a list of FlightSamples objects with the correct values.
    '''
    locked_now = datetime(2023, 6, 11, 13, 43)
    mock_dt.utcnow.return_value = locked_now
    mapper = FlightSamplesMapper()
    result = list(mapper.map_scatter_data(flight_data))
    expected_result = [
        FlightSamples(
            icao_id='abc123',
            sample_entry_date_utc=locked_now.replace(tzinfo=pytz.UTC),
            flight='123ABC',
            latitude=40.712776,
            longitude=-74.005974,
            altitude_ft=None,
            alt_change_ft_per_min=300,
            heading=120.5,
            ground_speed_knots=None,
            nav_modes="['autopilot']",
            emitter_category='A1',
            aircraft_type='B737',
            aircraft_registration='USA',
            flag='Military',
            source='adsb',
            rssi=-30,
            emergency='Emergency!'
        )
    ]
    assert len(result) == len(expected_result)
    result_dict = result[0].__dict__
    del result_dict['_sa_instance_state']
    expected_result_dict = expected_result[0].__dict__
    del expected_result_dict['_sa_instance_state']
    assert result_dict == expected_result_dict


def test_filter_flight(flight_data: list[dict]):
    '''
    Test that filter_flight returns True if the flight is valid and False if it is not.
    '''
    mapper = FlightSamplesMapper()
    valid_flight = mapper._filter_flight(flight_data[0])
    invalid_flight = mapper._filter_flight(flight_data[1])
    assert valid_flight is True
    assert invalid_flight is False


def test_map_flight(flight_data: list[dict]):
    '''
    Test that map_flight returns a FlightSamples object with the correct values.
    '''
    mapper = FlightSamplesMapper()
    result = mapper._map_flight(flight_data[0])
    expected_result = FlightSamples(
        icao_id='abc123',
        flight='123ABC',
        latitude=40.712776,
        longitude=-74.005974,
        altitude_ft=None,
        alt_change_ft_per_min=300,
        heading=120.5,
        ground_speed_knots=None,
        nav_modes="['autopilot']",
        emitter_category='A1',
        aircraft_type='B737',
        aircraft_registration='USA',
        flag='Military',
        source='adsb',
        rssi=-30,
        emergency='Emergency!'
    )
    result_dict = result.__dict__
    del result_dict['_sa_instance_state']
    expected_result_dict = expected_result.__dict__
    del expected_result_dict['_sa_instance_state']
    assert result_dict == expected_result_dict


def test_map_flight_geom_rate():
    '''
    Test that map_flight returns maps geom_rate to alt_change_ft_per_min if baro_rate is not an integer.
    '''
    flight_data = {
        'hex': 'abc123',
        'lat': '40.712776',
        'lon': '-74.005974',
        'geom_rate': '500',
    }
    mapper = FlightSamplesMapper()
    result = mapper._map_flight(flight_data)
    expected_result = FlightSamples(
        icao_id='abc123',
        flight=None,
        latitude=40.712776,
        longitude=-74.005974,
        altitude_ft=None,
        alt_change_ft_per_min=500,
        heading=None,
        ground_speed_knots=None,
        nav_modes='None',
        emitter_category=None,
        aircraft_type=None,
        aircraft_registration=None,
        flag=None,
        source=None,
        rssi=None,
        emergency=None,
    )
    result_dict = result.__dict__
    del result_dict['_sa_instance_state']
    expected_result_dict = expected_result.__dict__
    del expected_result_dict['_sa_instance_state']
    assert result_dict == expected_result_dict


def test_map_empty_list():
    '''
    Test that map_scatter_data returns an empty list if the input is an empty list.
    '''
    result = list(FlightSamplesMapper().map_scatter_data([]))
    expected_result = []
    assert result == expected_result
