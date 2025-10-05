from omegaconf import MISSING

from dataclasses import dataclass


@dataclass
class Flights:
    suppress_errors: bool = MISSING
    wait_between_runs: int = MISSING


@dataclass
class FlightsDev(Flights):
    suppress_errors: bool = False
    wait_between_runs: int = 120


@dataclass
class FlightsProd(Flights):
    suppress_errors: bool = True
    wait_between_runs: int = 1800


@dataclass
class FlightsStaging(Flights):
    suppress_errors: bool = True
    wait_between_runs: int = 1800
