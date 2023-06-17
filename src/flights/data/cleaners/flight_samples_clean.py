from flights.utils import logger

log = logger.create(__name__)


class FlightSamplesCleaner:
    '''
    Cleans a sample of flight scatter data to prepare for db model mapping.
    '''
    def clean_flight_sample(self, scatter_sample: list[dict]) -> list[dict]:
        '''
        Removes duplicates from geographic overlaps in the scatter data sample.
        '''
        log.info('cleaning duplicates from raw aircraft scatter data sample')
        unique_flights = {flight.get('hex'): flight for flight in scatter_sample}
        clean_flights = list(unique_flights.values())
        log.info(f'found {len(clean_flights)} unique flights in scatter data sample')
        log.debug(f'clean data:\n\n\n{clean_flights}\n\n\n')
        return clean_flights
