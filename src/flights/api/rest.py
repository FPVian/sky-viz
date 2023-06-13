from flights.utils import logger
from flights.config.settings import s

import requests

from typing import Optional, Any
import time

log = logger.create(__name__)


class RestApi:

    def __init__(self, url: str, headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {}

    def _make_request(self, method: str, params: Optional[dict] = None) -> Optional[requests.Response]:
        try:
            response = requests.request(method, self.url, params=params, headers=self.headers, timeout=s.api.timeout)
            response.raise_for_status()
            log.debug(f'api response:\n\n\n{response}\n\n\n')
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
        for _ in range(s.api.number_of_tries):
            response = self._make_request('GET', params)
            if response is not None and response.status_code == 200:
                log.debug(response.json())
                return response.json()
            time.sleep(s.api.wait_before_retry)
        log.critical(f'Failed to GET 200 status after {s.api.number_of_tries} tries. Url: {self.url} Params: {params}')
        if response:
            log.critical(f'Status code {response.status_code}, response text:\n{response.text}')
        return None
