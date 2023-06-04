from skyviz.utils import logger
from skyviz.config.groups.secrets import AdsbExchangeSecrets

import requests

from typing import Optional, Any
import time

log = logger.create(__name__)


class DemoData():

    def __init__(self) -> None:
        self.api_key: str = AdsbExchangeSecrets.api_key_dev

    def get_aircraft_scatter(self, lat: float, lon: float) -> list:
        log.info(f'Getting aircraft scatter data from AdsbExchange API at lat: {lat}, lon: {lon}')
        url = f'https://aircraftscatter.p.rapidapi.com/lat/{lat}/lon/{lon}/'
        headers = {
            'X-RapidAPI-Host': 'aircraftscatter.p.rapidapi.com',
            'X-RapidAPI-Key': self.api_key
        }
        response: dict[str, list] = BaseApi(url, headers).get()
        aircraft = None
        if response:
            aircraft = response.get('ac')
        if aircraft is None:
            log.warning('No aircraft scatter data returned')
            aircraft = []
        log.info(f'Found {len(aircraft)} aircraft scatter data points')
        return aircraft


class BaseApi:

    def __init__(self, url: str, headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {}

    def _make_request(self, method: str, params: Optional[dict] = None) -> Optional[requests.Response]:
        try:
            response = requests.request(method, self.url, params=params, headers=self.headers, timeout=3)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as error:
            self._log_error(error)
            return None

    def _log_error(self, error: requests.exceptions.RequestException):
        request = error.request
        response = error.response
        log.error(f'Error for {request.method} {request.url}: {error}')
        if response is not None:
            log.error(f'Status code {response.status_code}, response text:\n{response.text}')

    def get(self, params: Optional[dict] = None) -> Optional[Any]:
        for _ in range(3):
            response = self._make_request('GET', params)
            if response is not None and response.status_code == 200:
                log.debug(response.json())
                return response.json()
            time.sleep(60)
        log.critical(f'Failed to GET 200 status after {3} tries. Url: {self.url} Params: {params}')
        if response:
            log.critical(f'Status code {response.status_code}, response text:\n{response.text}')
        return None
