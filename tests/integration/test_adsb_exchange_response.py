from flights.utils import logger
from flights.config.settings import s
from flights.api.rest import BaseApi

log = logger.create(__name__)


def test_adsb_exchange_scatter_response_format():
    '''
    The ADSB Exchange Aircraft Scatter API must have 'ac' as a the key in the response
    If less items then the stated 'total' are returned, the method is not working properly
    '''
    url = 'https://aircraftscatter.p.rapidapi.com/lat/37.3387/lon/-122.8853/'
    headers = {
        'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
        'X-RapidAPI-Key': s.AdsbExchange.API_KEY
    }
    response: dict[str:list] = BaseApi(url, headers).get()
    log.debug(f'raw adsb exchange aircraft scatter response:\n{response}')
    assert 'ac' in response.keys()
    assert len(response['ac']) == response['total']


def test_adsb_exchange_traffic_response_format():
    '''
    The ADSB Exchange Aircraft Traffic API must have 'ac' as a the key in the response
    If less items then the stated 'total' are returned, the method is not working properly
    '''
    url = 'https://adsbx-flight-sim-traffic.p.rapidapi.com/api/aircraft/json/lat/37.3387/lon/-122.8853/dist/25/'
    headers = {
        'X-RapidAPI-Host': 'adsbx-flight-sim-traffic.p.rapidapi.com',
        'X-RapidAPI-Key': s.AdsbExchange.API_KEY
    }
    response: dict[str:list] = BaseApi(url, headers).get()
    log.debug(f'raw adsb exchange aircraft traffic response:\n{response}')
    assert 'ac' in response.keys()
    assert len(response['ac']) == response['total']
