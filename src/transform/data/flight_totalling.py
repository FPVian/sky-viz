from config.logger import Logger
from transform.data.base_calcs import BaseCalcs


log = Logger.create(__name__)


class FlightTotaller(BaseCalcs):
    '''
    Populates flight totals tables for efficiently presenting historic trends.
    '''
    def aggregate_daily_totals():
        pass

    def aggregate_weekly_totals():
        pass

    def aggregate_monthly_totals():
        pass
