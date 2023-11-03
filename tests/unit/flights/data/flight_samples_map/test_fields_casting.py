from flights.data.flight_samples_map import FlightSamplesMapper

from unittest.mock import patch


def test_map_flag():
    '''
    Test that the _map_flag method converts the dbFlags value to a human readable string.
    '''
    flight_data = {
        'hex': 'abc123',
        'lat': '40.712776',
        'lon': '-74.005974',
        'dbFlags': '8',
    }
    result = FlightSamplesMapper()._map_flag(flight_data)
    assert result == 'LADD'


def test_map_emergency_with_emergency_and_squawk():
    '''
    Test that the _map_emergency method combines the emergency and squawk fields when both are present.
    '''
    flight_data = {
        'hex': 'abc123',
        'lat': '40.712776',
        'lon': '-74.005974',
        'emergency': 'emergency',
        'squawk': '7600'
    }
    result = FlightSamplesMapper()._map_emergency(flight_data)
    assert result == 'Radio Failure! emergency'


def test_map_emergency_with_emergency_only():
    '''
    Test that the _map_emergency method maps the emergency field when there is no squawk present.
    '''
    flight_data = {
        'hex': 'abc123',
        'lat': '40.712776',
        'lon': '-74.005974',
        'emergency': 'emergency',
    }
    result = FlightSamplesMapper()._map_emergency(flight_data)
    assert result == 'emergency'


def test_map_emergency_with_squawk_only():
    '''
    Test that the _map_emergency method converts the emergency squawk a human readable string.
    '''
    flight_data = {
        'hex': 'abc123',
        'lat': '40.712776',
        'lon': '-74.005974',
        'squawk': '7600'
    }
    result = FlightSamplesMapper()._map_emergency(flight_data)
    assert result == 'Radio Failure!'


def test_safe_cast_to_int_with_int():
    '''
    Test that _safe_cast_to_int returns an int when given a string representation of an int.
    '''
    result = FlightSamplesMapper()._safe_cast_to_int('133')
    assert result == 133


@patch('flights.data.flight_samples_map.log')
def test_safe_cast_to_int_with_letters(mock_log):
    '''
    Test that the _safe_cast_to_int method returns None 
    and logs a warning when given a string that cannot be cast to an int.
    '''
    result = FlightSamplesMapper()._safe_cast_to_int('not a number')
    assert result == None
    assert mock_log.warning.call_count == 1


def test_safe_cast_to_float_with_number():
    '''
    Test that _safe_cast_to_float returns a float when given a string representation of a float.
    '''
    result = FlightSamplesMapper()._safe_cast_to_float('133.532')
    assert result == 133.532


@patch('flights.data.flight_samples_map.log')
def test_safe_cast_to_float_with_letters(mock_log):
    '''
    Test that the _safe_cast_to_float method returns None 
    and logs a warning when given a string that cannot be cast to a float.
    '''
    result = FlightSamplesMapper()._safe_cast_to_float('not a number')
    assert result == None
    assert mock_log.warning.call_count == 1
