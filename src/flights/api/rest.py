from flights.utils import logger

import requests

from typing import Optional

log = logger.create(__name__)

NUMBER_OF_TRIES = 3


class BaseApi:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, headers: Optional[str] = None, params: Optional[str] = None):
        url = self.base_url + endpoint
        response = requests.get(url, headers=headers, params=params, timeout=5)
        for _ in range(NUMBER_OF_TRIES):
            if response.status_code == 200:
                return response.json()
            try:
                response.raise_for_status()
                log.warning(f'Got status code {response.status_code} from {url}')
                log.warning(f'response.text: {response.text}')
            except requests.exceptions.HTTPError as e:
                log.error(f'HTTPError: {e}')
                log.error(f'HTTP Status Code: {e.response.status_code}')
                log.error(f'Response: {e.response.text}')
                log.error(f'Response headers: {e.response.headers}')
                log.error(f'Request url: {e.response.request.url}')
                log.error(f'Request method: {e.response.request.method}')
        raise ConnectionAbortedError(f'Failed to get {url} after {NUMBER_OF_TRIES} tries')
