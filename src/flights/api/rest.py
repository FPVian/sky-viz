from flights.utils import logger

import requests

from typing import Optional

log = logger.create(__name__)

NUMBER_OF_TRIES = 5


class BaseApi:
    def __init__(self, url: str, headers: Optional[str] = None):
        self.url = url
        self.headers = headers

    def get(self, params: Optional[str] = None) -> requests.Response or None:
        response = requests.get(self.url, headers=self.headers, params=params, timeout=5)
        for _ in range(NUMBER_OF_TRIES):
            if response.status_code == 200:
                return response.json()
            try:
                response.raise_for_status()
                log.warning(f'Got status code {response.status_code} from {self.url}')
                log.warning(f'response.text: {response.text}')
            except requests.exceptions.HTTPError as e:
                log.error(f'HTTPError: {e}')
                log.error(f'HTTP Status Code: {e.response.status_code}')
                log.error(f'Response: {e.response.text}')
                log.error(f'Response headers: {e.response.headers}')
                log.error(f'Request url: {e.response.request.url}')
                log.error(f'Request method: {e.response.request.method}')
        log.critical(f'Failed to get response from {self.url} after {NUMBER_OF_TRIES} tries')
