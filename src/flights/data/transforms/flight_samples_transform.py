from flights.utils import logger
from database.models import FlightSamples

from datetime import datetime
from typing import Iterator
import pytz

log = logger.create(__name__)


class FlightSamplesTransform:
    '''
    Transforms a sample of flight scatter data into a format that is ready for db insertion.
    '''
    def transform_flight_sample(
            self, flight_sample: Iterator[FlightSamples]) -> Iterator[FlightSamples]:
        '''
        Adds a sample collection date to each mapped row of the flight sample.
        '''
        log.info('transforming mapped flight samples table data')
        sample_collection_date = datetime.utcnow().replace(tzinfo=pytz.utc)
        for table_row in flight_sample:
            table_row.sample_entry_date_utc = sample_collection_date
            yield table_row
        log.info('transformed mapped flight samples table data')
