from flights.utils import logger
from flights.config.settings import s
from flights.api.rest import BaseApi

from typing import Optional

log = logger.create(__name__)


class AdsbExchangeClient():

    def get_aircraft_scatter(self, lat: float, lon: float):
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
        base_url = 'https://aircraftscatter.p.rapidapi.com/lat/{lat}/lon/{lon}/'
        headers = {
            'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
            'X-RapidAPI-Key': s.AdsbExchange.API_KEY
        }
        url = base_url.format(lat=str(lat), lon=str(lon))
        response: dict = BaseApi(url, headers).get()
        aircraft: list[dict] = response['ac'] if response['ac'] is not None else []
        log.info(f'Found {len(aircraft)} aircraft data points')
        return aircraft

    def get_aircraft_traffic(self, lat: float, lon: float):
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
        base_url = 'https://adsbx-flight-sim-traffic.p.rapidapi.com/api/aircraft/json/lat/{lat}/lon/{lon}/dist/25/'
        headers = {
            'X-RapidAPI-Host': 'adsbx-flight-sim-traffic.p.rapidapi.com',
            'X-RapidAPI-Key': s.AdsbExchange.API_KEY
        }
        url = base_url.format(lat=str(lat), lon=str(lon))
        response: dict = BaseApi(url, headers).get()
        aircraft: list[dict] = response['ac'] if response['ac'] is not None else []
        log.info(f'Found {len(aircraft)} aircraft traffic data points')
        return aircraft


# testing
from pprint import pprint
# pprint(AdsbExchangeClient().get_aircraft_traffic(90, 45))
pprint(AdsbExchangeClient().get_aircraft_traffic(51.533, -0.0926))
# test that list length = 'total'
# test outcome for empty response ([])
# test raise Key Error if 'ac' is missing
