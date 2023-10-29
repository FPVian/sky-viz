from transform.utils.logger import Logger
from database.models import FlightSamples, FlightAggregates
from transform.db.base_repo import BaseRepository

from sqlalchemy.orm import Session

from typing import Iterator
from datetime import datetime, date, timedelta

log = Logger.create(__name__)


class FlightsProcessor:
    '''
    Populates tables for running analytics on flight data.
    '''
    def summarize_flight_samples(self, session: Session, db: BaseRepository) -> None:
        '''
        Gets new flight samples, summarizes them, and inserts them into the flight_aggregates table.
        '''
        log.info('summarizing flight samples')
        flight_samples: Iterator[FlightSamples] = db.get_new_flight_samples(session)
        aggregate_rows: list[FlightAggregates] = []
        for flight_sample in flight_samples:
            sample_date: datetime = flight_sample.sample_entry_date_utc
            log.info(f'summarizing flight sample from: {sample_date}')
            aggregate_row = FlightAggregates(
                sample_entry_date_utc=sample_date,
                number_of_flights=db.count_flight_samples_by_date(session, sample_date),
            )
            aggregate_rows.append(aggregate_row)
        log.info(f'summarized {len(aggregate_rows)} flight samples')
        db.insert_rows(session, aggregate_rows)

    '''
    Control flow:

    find sample dates with no matching daily aggregates
        if missing daily aggregates:
            summarize_daily_top_flights()

    find sample dates with no matching weekly aggregates
        if missing weekly aggregates:
            summarize_weekly_monthly_top_flights()

    find sample dates with no matching monthly aggregates
        if missing monthly aggregates:
            summarize_weekly_monthly_top_flights()
            count_flights_per_month()
    '''

    def summarize_daily_top_flights(self, entry_date: date) -> None:
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
    
    def summarize_weekly_monthly_top_flights(self, start_date: datetime, end_date: datetime) -> None:
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