from omegaconf import MISSING

from dataclasses import dataclass
from pathlib import Path


@dataclass
class General:
    project_root: Path = Path(__file__).resolve().parents[4]
    cache_time_to_live_min: int = MISSING


@dataclass
class GeneralDev(General):
    cache_time_to_live_min: int = 2


@dataclass
class GeneralStaging(General):
    cache_time_to_live_min: int = 0


@dataclass
class GeneralProd(General):
    cache_time_to_live_min: int = 30
