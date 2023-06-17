from flights.config.groups.secrets import AdsbExchangeSecrets

from dataclasses import dataclass, field


@dataclass
class AdsbExchange:
    api_key: str
    usa_sample_coordinates: list = field(default_factory=lambda: [
        (43, -119),
        (43, -105.5),
        (43, -92),
        (43, -78.5),
        (31, -119),
        (31, -106),
        (31, -93),
        (31, -80),
    ])


@dataclass
class AdsbExchangeDev(AdsbExchange):
    api_key: str = AdsbExchangeSecrets.api_key_dev


@dataclass
class AdsbExchangeProd(AdsbExchange):
    api_key: str = AdsbExchangeSecrets.api_key_prod
