from flights.config.groups.secrets import AdsbExchangeSecrets

from dataclasses import dataclass


@dataclass
class AdsbExchange:
    api_key: str
    

@dataclass
class AdsbExchangeDev(AdsbExchange):
    api_key: str = AdsbExchangeSecrets.api_key_dev


@dataclass
class AdsbExchangeProd(AdsbExchange):
    api_key: str = AdsbExchangeSecrets.api_key_prod
