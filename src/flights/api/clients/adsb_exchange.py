from flights.utils import logger
from flights.config.settings import s
from flights.api.rest import BaseApi

log = logger.create(__name__)


class AdsbExchangeClient():

    def __init__(self) -> None:
        self.api_key: str = s.AdsbExchange.API_KEY

    def get_aircraft_scatter(self, lat: float, lon: float) -> list[dict] or None:
        '''
        Returns a dict of aircraft within 1,000 km of a given lat/lon, flying at an elevation of 10,000 feet or higher.
        Response is in the following format:
            [{'alt_baro': 'ground',
            'category': 'C0',
            'dst': 549.96,
            'flight': 'TXLU01  ',
            'hex': '49f0e0',
            'lat': 50.115556,
            'lon': 14.268085,
            'messages': 126719,
            'mlat': [],
            'nac_p': 11,
            'nic': 11,
            'rc': 8,
            'rssi': -25.3,
            'seen': 3.3,
            'seen_pos': 3.324,
            'sil': 2,
            'sil_type': 'unknown',
            'tisb': [],
            'type': 'adsb_icao_nt',
            'version': 0}]
        '''
        log.info(f'Getting aircraft scatter data from AdsbExchange API at lat: {lat}, lon: {lon}')
        url = f'https://aircraftscatter.p.rapidapi.com/lat/{lat}/lon/{lon}/'
        headers = {
            'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
            'X-RapidAPI-Key': self.api_key
        }
        response: dict[str:list] = BaseApi(url, headers).get()
        aircraft = response.get('ac')
        log.info(f'Found {len(aircraft)} aircraft data points')
        return aircraft

    def get_aircraft_traffic(self, lat: float, lon: float) -> list[dict] or None:
        '''
        Returns a dict of all aircraft within 25 nautical mile radius of a given lat/lon.
        Response is in the following format:
            [{'alt': '',
            'altt': '0',
            'call': 'LEADER8',
            'cou': 'United Kingdom',
            'dst': '23.07',
            'galt': '',
            'gnd': '1',
            'icao': '43BFDD',
            'interested': '0',
            'lat': '51.152251',
            'lon': '-0.178776',
            'mil': '0',
            'mlat': '0',
            'opicao': '',
            'pos': '1',
            'postime': '1684713731849',
            'reg': '',
            'sat': '0',
            'spd': '5.2',
            'sqk': '',
            'talt': '',
            'tisb': '0',
            'trak': '281.2',
            'trkh': '0',
            'trt': '3',
            'ttrk': '',
            'type': '',
            'vsi': '',
            'vsit': '0',
            'wtc': '0'}]
        '''
        log.info(f'Getting aircraft traffic data from AdsbExchange API at lat: {lat}, lon: {lon}')
        url = f'https://adsbx-flight-sim-traffic.p.rapidapi.com/api/aircraft/json/lat/{lat}/lon/{lon}/dist/25/'
        headers = {
            'X-RapidAPI-Host': 'adsbx-flight-sim-traffic.p.rapidapi.com',
            'X-RapidAPI-Key': self.api_key
        }
        response: dict[str:list] = BaseApi(url, headers).get()
        aircraft = response.get('ac')
        log.info(f'Found {len(aircraft)} aircraft traffic data points')
        return aircraft
