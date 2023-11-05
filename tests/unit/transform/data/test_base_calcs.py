from transform.data.base_calcs import BaseCalcs
from database.models import FlightSamples

import polars as pl

from datetime import datetime



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
    result = BaseCalcs()._filter_to_max_row(flight_sample, FlightSamples.altitude_ft)
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
    result = BaseCalcs()._filter_to_min_row(flight_sample, FlightSamples.altitude_ft)
    assert result[FlightSamples.icao_id.name].item() in ['ccc333', 'bbb222']