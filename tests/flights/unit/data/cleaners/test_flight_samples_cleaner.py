from flights.data.cleaners.flight_samples_clean import FlightSamplesCleaner


def test_clean_flight_sample():
    '''
    Test that the resulting list of flights is unique by hex.
    The expected result contains the last entry for each hex because the earlier entries are overwritten.
    '''
    sample_data = [
        {'hex': 'abc', 'other_data': 'data1'},
        {'hex': 'def', 'other_data': 'data2'},
        {'hex': 'abc', 'other_data': 'data3'},
        {'hex': 'ghi', 'other_data': 'data4'},
        {'hex': 'def', 'other_data': 'data5'},
        {'other_data': 'data6'},
        {'other_data': 'data7'},
    ]
    expected_result = [
        {'hex': 'abc', 'other_data': 'data3'},
        {'hex': 'def', 'other_data': 'data5'},
        {'hex': 'ghi', 'other_data': 'data4'},
        {'other_data': 'data7'},
    ]
    cleaned_data = FlightSamplesCleaner().clean_flight_sample(sample_data)
    assert cleaned_data == expected_result


def test_clean_flight_sample_without_data():
    '''
    Test that clean_flight_sample returns an empty list if the input is an empty list.
    '''
    cleaned_data = FlightSamplesCleaner().clean_flight_sample([])
    assert cleaned_data == []
