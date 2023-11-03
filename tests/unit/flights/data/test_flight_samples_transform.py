from flights.data.flight_samples_transform import FlightSamplesTransform
from database.models import FlightSamples

from datetime import datetime
import pytz


def test_transform_flight_sample_adds_timestamp():
    '''
    Test that the transform_flight_sample method adds the current time to each row of the flight sample.
    Test that the sample_entry_date for all rows in the sample is the same.
    '''
    flight_sample = iter([FlightSamples(), FlightSamples()])
    test_start_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    transformed_sample = FlightSamplesTransform().transform_flight_sample(flight_sample)
    transformed_sample = list(transformed_sample)

    assert len(transformed_sample) == 2
    assert transformed_sample[0].sample_entry_date_utc == transformed_sample[1].sample_entry_date_utc
    for flight_samples_row in transformed_sample:
        assert flight_samples_row.sample_entry_date_utc > test_start_time


def test_transform_flight_sample_without_data():
    '''
    Test that the transform_flight_sample method returns an empty iterator when no data is provided.
    '''
    flight_sample = iter([])
    transformed_sample = FlightSamplesTransform().transform_flight_sample(flight_sample)

    assert list(transformed_sample) == []
    assert next(transformed_sample, None) is None
