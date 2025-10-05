from config.logger import Logger

from datetime import datetime, date, timedelta

log = Logger.create(__name__)


class AircraftRanker:
    '''
    Populates top aircraft tables for running analytics on the most common aircraft.
    '''
    def summarize_daily_top_aircraft(self, entry_date: date) -> None:
        end_date = entry_date + timedelta(days=1)
        '''
        date = date
        avg_count_aircraft_type_per_sample()
        join 
        count_num_flights_by_aircraft_type()
        join
        count_unique_aircraft_by_aircraft_type
        insert into db
        '''

    def summarize_weekly_monthly_top_aircraft(self, start_date: datetime, end_date: datetime) -> None:
        pass
        '''
        date = date
        avg_count_aircraft_type_per_sample()
        join 
        !!! write function to sum daily totals
        join
        count_unique_aircraft_by_aircraft_type
        insert into db
        '''