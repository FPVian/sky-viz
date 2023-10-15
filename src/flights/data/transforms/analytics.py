from flights.config.settings import s
from flights.utils import logger
from database.models import FlightSamples, FlightAggregates
from flights.db.base_repo import BaseRepository

from sqlalchemy.orm import Session

from typing import Iterator
from datetime import datetime

log = logger.create(__name__)

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
            aggregate_row: FlightAggregates = FlightAggregates()
            sample_date: datetime = flight_sample.sample_entry_date_utc
            log.info(f'summarizing flight sample from: {sample_date}')
            aggregate_row.sample_entry_date_utc = sample_date
            aggregate_row.number_of_flights = db.count_flight_samples_by_date(session, sample_date)
            aggregate_rows.append(aggregate_row)
        log.info(f'summarized {len(aggregate_rows)} flight samples')
        db.insert_rows(session, aggregate_rows)
