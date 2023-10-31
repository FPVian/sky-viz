from omegaconf import MISSING

from dataclasses import dataclass


@dataclass
class Transform:
    suppress_errors: bool = MISSING
    wait_between_runs: int = MISSING


@dataclass
class TransformDev(Transform):
    suppress_errors: bool = False
    wait_between_runs: int = 120


@dataclass
class TransformProd(Transform):
    suppress_errors: bool = True
    wait_between_runs: int = 1800


@dataclass
class TransformStaging(Transform):
    suppress_errors: bool = True
    wait_between_runs: int = 1800
