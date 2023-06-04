from flights.config.env import Environs

from omegaconf import MISSING

from dataclasses import dataclass
from pathlib import Path


@dataclass
class General:
    project_root: Path = Environs.project_root
    suppress_errors: bool = MISSING


@dataclass
class GeneralDev(General):
    suppress_errors: bool = False


@dataclass
class GeneralProd(General):
    suppress_errors: bool = True
