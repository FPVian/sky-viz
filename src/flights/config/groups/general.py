from omegaconf import MISSING

from dataclasses import dataclass
from pathlib import Path


@dataclass
class General:
    project_root: Path = Path(__file__).resolve().parents[4]
    suppress_errors: bool = MISSING
    wait_between_runs: int = MISSING


@dataclass
class GeneralDev(General):
    suppress_errors: bool = False
    wait_between_runs: int = 120


@dataclass
class GeneralProd(General):
    suppress_errors: bool = True
    wait_between_runs: int = 1800
