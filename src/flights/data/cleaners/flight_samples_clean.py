from flights.utils import logger

log = logger.create(__name__)


class FlightSamplesCleaner:
    '''
    Cleans a sample of flight scatter data to prepare for db model mapping.
    '''
    def clean_flight_sample(self, scatter_sample: list) -> list:
        '''
        Removes duplicates from geographic overlaps in the scatter data sample.
        '''
        log.info('cleaning duplicates from raw aircraft scatter data sample')
        clean_flights = []
        flight_index = {}
        for flight in scatter_sample:
            if flight['hex'] not in flight_index:
                flight_index[flight['hex']] = 'already found'
                clean_flights.append(flight)
        log.info(f'cleaned {len(clean_flights)} unique flights from scatter data sample')
        log.debug(f'clean data:\n\n\n{clean_flights}\n\n\n')
        return clean_flights
