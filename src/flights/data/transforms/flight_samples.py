from flights.utils import logger
from database.models import FlightSamples

from datetime import datetime
from typing import Iterator

log = logger.create(__name__)


class FlightSamplesTransform:
    '''
    Takes data mapped to the flight samples table model and transforms it into a format that can be used for visualizations.
    '''
    def transform_flight_sample(self, flight_sample: Iterator[FlightSamples], sample_entry_date: datetime) -> list[FlightSamples]:
        log.info('starting get_current_flights')
        flights = []
        for table_row in flight_sample:
            table_row.sample_entry_date_utc = sample_entry_date
            flights.append(table_row)
        self._remove_duplicates()
        log.info(f'mapped {len(flights)} rows of scatter data to flights table model')
        log.debug(f'transformed data:\n\n\n{[flight.__dict__ for flight in flights]}\n\n\n')
        return flights

    def _remove_duplicates(self):
        pass
