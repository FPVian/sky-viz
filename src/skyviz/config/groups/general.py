from skyviz.config.env import Environs

from dataclasses import dataclass
from pathlib import Path


@dataclass
class General:
    project_root: Path = Environs.project_root


@dataclass
class GeneralDev(General):
    pass


@dataclass
class GeneralProd(General):
    pass
