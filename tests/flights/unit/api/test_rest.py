from config.settings import s
from flights.api.rest import RestApi

from unittest.mock import patch, Mock
from requests.exceptions import ConnectionError, Timeout


@patch('requests.request')
def test_get_success(mock_request):
    '''
    Test that get() returns the json from the response when the status code is 200
    '''
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = {'result': 'success'}
    response = RestApi('https://fakeurl.com').get()
    assert response == {'result': 'success'}
    assert mock_request.call_count == 1


@patch('flights.api.rest.log')
@patch('requests.request')
def test_get_failure(mock_request, mock_log):
    '''
    Test that get() returns None when the status code is not 200 and
    logs the response after a preset # of retries.
    '''
    mock_request.return_value.status_code = 204
    response = RestApi('https://fakeurl2.com').get()
    assert mock_request.call_count == s.api.number_of_tries
    assert mock_log.critical.call_count == 2
    assert response is None


@patch('flights.api.rest.RestApi._log_error')
@patch('requests.request')
def test_get_request_errors(mock_request, mock_log_error):
    '''
    Test that get() logs errors from networking issues and tries until status code is 200
    '''
    mock_get_success = Mock(status_code=200)
    mock_get_success.json.return_value = {'result': 'success'}
    mock_request.side_effect = [ConnectionError, Timeout, mock_get_success]
    response = RestApi('https://fakeurl3.com').get()
    assert mock_request.call_count == 3
    assert mock_log_error.call_count == 2
    assert response == {'result': 'success'}
