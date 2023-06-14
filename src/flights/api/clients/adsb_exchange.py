from flights.utils import logger
from flights.config.settings import s
from flights.api.rest import RestApi

log = logger.create(__name__)


class AdsbExchangeClient():
    '''
    Handles calls to AdsbExchange API.
    Fields reference: https://www.adsbexchange.com/version-2-api-wip/
    '''
    def __init__(self) -> None:
        self.api_key: str = s.api.adsb_exchange.api_key

    def get_aircraft_scatter(self, latitude: float, longitude: float) -> list:
        '''
        Returns a dict of aircraft within 1,000 km of a given lat/lon, flying at an elevation of 10,000 feet or higher.
        Rate limit: 10 requests/min, 60,000 requests/month

        Response is in the following format:
            [{'alert': 1,
            'alt_baro': 33975,
            'alt_geom': 34650,
            'baro_rate': 224,
            'category': 'A5',
            'dst': 546.24,
            'emergency': 'none',
            'flight': 'LOT5H   ',
            'geom_rate': 0,
            'gs': 478.4,
            'gva': 2,
            'hex': '48ae21',
            'ias': 295,
            'lat': 52.401713,
            'lon': 14.422852,
            'mach': 0.844,
            'mag_heading': 277.21,
            'messages': 632825,
            'mlat': [],
            'nac_p': 9,
            'nac_v': 2,
            'nav_altitude_mcp': 34016,
            'nav_heading': 281.95,
            'nav_modes': ['autopilot', 'vnav', 'lnav', 'tcas'],
            'nav_qnh': 1012.8,
            'nic': 8,
            'nic_baro': 1,
            'oat': -53,
            'r': 'SP-LSB',
            'rc': 186,
            'roll': -2.11,
            'rssi': -12.1,
            'sda': 2,
            'seen': 0,
            'seen_pos': 0,
            'sil': 3,
            'sil_type': 'perhour',
            'spi': 0,
            'squawk': '3547',
            't': 'B789',
            'tas': 488,
            'tat': -22,
            'tisb': [],
            'track': 280.11,
            'track_rate': -0.09,
            'true_heading': 282.27,
            'type': 'adsb_icao',
            'version': 2,
            'wd': 343,
            'ws': 20},]
        '''
        log.info(f'Getting aircraft scatter data from AdsbExchange API at lat: {latitude}, lon: {longitude}')
        url = f'https://aircraftscatter.p.rapidapi.com/lat/{latitude}/lon/{longitude}/'
        headers = {
            'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
            'X-RapidAPI-Key': self.api_key
        }
        response: dict[str, list] = RestApi(url, headers).get()
        aircraft = None
        if response:
            aircraft = response.get('ac')
        if aircraft is None:
            log.warning('No aircraft scatter data returned')
            aircraft = []
        log.info(f'Found {len(aircraft)} aircraft scatter data points')
        return aircraft

    def get_aircraft_traffic(self, latitude: float, longitude: float) -> list:
        '''
        Returns a dict of all aircraft within 25 nautical mile radius of a given lat/lon.
        Rate limit: 5,760 requests/month

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
        log.info(f'Getting aircraft traffic data from AdsbExchange API at lat: {latitude}, lon: {longitude}')
        url = f'https://adsbx-flight-sim-traffic.p.rapidapi.com/api/aircraft/json/lat/{latitude}/lon/{longitude}/dist/25/'
        headers = {
            'X-RapidAPI-Host': 'adsbx-flight-sim-traffic.p.rapidapi.com',
            'X-RapidAPI-Key': self.api_key
        }
        response: dict[str, list] = RestApi(url, headers).get()
        aircraft = None
        if response:
            aircraft = response.get('ac')
        if aircraft is None:
            log.warning('No aircraft traffic data returned')
            aircraft = []
        log.info(f'Found {len(aircraft)} aircraft traffic data points')
        return aircraft
