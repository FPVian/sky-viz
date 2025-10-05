from config.groups.api_subgroup.adsb_exchange import AdsbExchange

from omegaconf import MISSING

from dataclasses import dataclass


@dataclass
class Api:
    timeout: int = MISSING
    number_of_tries: int = MISSING
    wait_before_retry: int = MISSING
    adsb_exchange: AdsbExchange = MISSING
    

@dataclass
class ApiDev(Api):
    timeout: int = 1
    number_of_tries: int = 3
    wait_before_retry: int = 0


@dataclass
class ApiProd(Api):
    timeout: int = 5
    number_of_tries: int = 5
    wait_before_retry: int = 60
