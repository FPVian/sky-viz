from skyviz.config.env import Environs

from omegaconf import MISSING

from dataclasses import dataclass
from pathlib import Path


@dataclass
class General:
    project_root: Path = Environs.project_root
    cache_time_to_live_min: int = MISSING


@dataclass
class GeneralDev(General):
    cache_time_to_live_min: int = 1


@dataclass
class GeneralProd(General):
    cache_time_to_live_min: int = 30
