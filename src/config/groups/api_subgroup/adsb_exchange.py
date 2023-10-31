from omegaconf import MISSING

from dataclasses import dataclass, field
import os
from typing import Optional


@dataclass
class AdsbExchange:
    api_key_env_var: str = MISSING
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
    api_key_env_var: str = 'ADSB_EXCHANGE_API_KEY_DEV'
    api_key: Optional[str] = os.environ.get(api_key_env_var)


@dataclass
class AdsbExchangeProd(AdsbExchange):
    api_key_env_var: str = 'ADSB_EXCHANGE_API_KEY_PROD'
    api_key: Optional[str] = os.environ.get(api_key_env_var)


@dataclass
class AdsbExchangeStaging(AdsbExchange):
    api_key_env_var: str = 'ADSB_EXCHANGE_API_KEY_DEV'
    api_key: Optional[str] = os.environ.get(api_key_env_var)


@dataclass
class AdsbExchangeTest(AdsbExchange):
    api_key_env_var: str = 'ADSB_EXCHANGE_API_KEY_DEV'
    api_key: Optional[str] = os.environ.get(api_key_env_var)
    usa_sample_coordinates: list = field(default_factory=lambda: [(43, -105.5), (31, -106)])
