from flights.utils import logger
from database.models import FlightSamples

from datetime import datetime
from typing import Iterator

log = logger.create(__name__)


class FlightSamplesTransform:
    '''
    Transforms a sample of flight scatter data into a format that is ready for db insertion.
    '''
    def transform_flight_sample(
            self, flight_sample: Iterator[FlightSamples], sample_entry_date: datetime
    ) -> list[FlightSamples]:
        '''
        Adds the sample collection date to each mapped row of the flight sample.
        '''
        log.info('transforming mapped flights samples table data')
        flights = []
        for table_row in flight_sample:
            table_row.sample_entry_date_utc = sample_entry_date
            flights.append(table_row)
        log.info(f'mapped {len(flights)} rows of scatter data to flights table model')
        log.debug(f'transformed data:\n\n\n{[flight.__dict__ for flight in flights]}\n\n\n')
        return flights
