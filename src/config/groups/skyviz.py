from omegaconf import MISSING

from dataclasses import dataclass


@dataclass
class Skyviz:
    cache_time_to_live_min: int = MISSING
    time_zone: str = 'US/Central'


@dataclass
class SkyvizDev(Skyviz):
    cache_time_to_live_min: int = 2


@dataclass
class SkyvizProd(Skyviz):
    cache_time_to_live_min: int = 5


@dataclass
class SkyvizStaging(Skyviz):
    cache_time_to_live_min: int = 0
