from config.logger import Logger
from config.settings import Settings
from flights.api.rest import RestApi

import pytest

log = Logger.create(__name__)


@pytest.fixture
def cfg():
    return Settings().build_config(overrides=['api/adsb_exchange=adsb_exchange_test'])


def test_adsb_exchange_scatter_response_format(cfg) -> None:
    '''
    The ADSB Exchange Aircraft Scatter API must have 'ac' as a the key in the response
    If less items then the stated 'total' are returned, the method is not working properly
    '''
    url = 'https://aircraftscatter.p.rapidapi.com/lat/37.3387/lon/-122.8853/'
    headers = {
        'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
        'X-RapidAPI-Key': cfg.api.adsb_exchange.api_key
    }
    print(headers)
    response: dict[str, list] = RestApi(url, headers).get()
    log.debug(f'raw adsb exchange aircraft scatter response:\n{response}')
    assert 'ac' in response.keys()
    if response['ac'] is not None:
        assert len(response['ac']) == response['total']
    else:
        assert response['total'] == 0


def test_adsb_exchange_traffic_response_format(cfg) -> None:
    '''
    The ADSB Exchange Aircraft Traffic API must have 'ac' as a the key in the response
    If less items then the stated 'total' are returned, the method is not working properly
    '''
    url = ('https://adsbx-flight-sim-traffic.p.rapidapi.com/'
           + 'api/aircraft/json/lat/37.3387/lon/-122.8853/dist/25/')
    headers = {
        'X-RapidAPI-Host': 'adsbx-flight-sim-traffic.p.rapidapi.com',
        'X-RapidAPI-Key': cfg.api.adsb_exchange.api_key
    }
    response: dict[str, list] = RestApi(url, headers).get()
    log.debug(f'raw adsb exchange aircraft traffic response:\n{response}')
    assert 'ac' in response.keys()
    if response['ac'] is not None:
        assert len(response['ac']) == response['total']
    else:
        assert response['total'] == 0
