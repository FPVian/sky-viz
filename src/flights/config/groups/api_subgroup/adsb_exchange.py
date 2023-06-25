from omegaconf import MISSING

from dataclasses import dataclass, field
import os
from typing import Optional


@dataclass
class AdsbExchange:
    api_key: Optional[str] = MISSING
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
    api_key: Optional[str] = os.environ.get('ADSB_EXCHANGE_API_KEY_DEV')


@dataclass
class AdsbExchangeProd(AdsbExchange):
    api_key: Optional[str] = os.environ.get('ADSB_EXCHANGE_API_KEY_PROD')


@dataclass
class AdsbExchangeTest(AdsbExchange):
    api_key: Optional[str] = os.environ.get('ADSB_EXCHANGE_API_KEY_DEV')
    usa_sample_coordinates: list = field(default_factory=lambda: [(43, -105.5), (31, -106)])
