from database.models import FlightSamples
from config.logger import Logger

from typing import Optional, Iterator
from datetime import datetime
import pytz

log = Logger.create(__name__)


class FlightSamplesMapper:
    '''
    Takes the cleaned scatter data from ADSB exchange and maps it to the flight samples table model.
    '''
    def map_scatter_data(self, scatter_data: list[dict]) -> Iterator[FlightSamples]:
        log.info(f'mapping {len(scatter_data)} rows of scatter data to flight samples table model')
        scatter_sample = self._dedupe_flight_sample(scatter_data)
        log.info('filtering out irrelevant scatter data')
        filtered_flights = filter(self._filter_flight, scatter_sample)
        flights = map(self._map_flight, filtered_flights)
        flights_with_date: Iterator[FlightSamples] = self._add_sample_date(flights)
        log.info('mapped scatter data to flight samples table model')
        return flights_with_date
    
    def _dedupe_flight_sample(self, scatter_sample: list[dict]) -> list[dict]:
        '''
        Removes duplicates from geographic overlaps in the scatter data sample.
        '''
        log.info('cleaning duplicates from raw aircraft scatter data sample')
        unique_flights = {flight.get('hex'): flight for flight in scatter_sample}
        clean_flights = list(unique_flights.values())
        log.info(f'found {len(clean_flights)} unique flights in scatter data sample')
        log.debug(f'clean data:\n\n\n{clean_flights}\n\n\n')
        return clean_flights

    def _filter_flight(self, flight: dict) -> bool:
        valid_flight = all([flight.get('alt_baro') != 'ground',
                            flight.get('hex'),
                            self._safe_cast_to_float(flight.get('lat')),
                            self._safe_cast_to_float(flight.get('lon')),
                            ])
        return valid_flight

    def _map_flight(self, flight: dict) -> FlightSamples:
        table_row = FlightSamples()
        table_row.icao_id = flight['hex']
        table_row.flight = flight.get('flight')
        table_row.latitude = self._safe_cast_to_float(flight['lat'])
        table_row.longitude = self._safe_cast_to_float(flight['lon'])
        table_row.altitude_ft = self._safe_cast_to_int(flight.get('alt_baro'))

        table_row.alt_change_ft_per_min = self._safe_cast_to_int(flight.get('baro_rate'))
        if table_row.alt_change_ft_per_min is None:
            table_row.alt_change_ft_per_min = self._safe_cast_to_int(flight.get('geom_rate'))

        table_row.heading = self._safe_cast_to_float(flight.get('track'))
        table_row.ground_speed_knots = self._safe_cast_to_float(flight.get('gs'))
        table_row.nav_modes = str(flight.get('nav_modes'))
        table_row.emitter_category = flight.get('category')
        table_row.aircraft_type = flight.get('t')
        table_row.aircraft_registration = flight.get('r')
        table_row.flag = self._map_flag(flight)
        table_row.source = flight.get('type')
        table_row.rssi = self._safe_cast_to_float(flight.get('rssi'))
        table_row.emergency = self._map_emergency(flight)
        return table_row
    
    def _map_flag(self, flight: dict) -> Optional[str]:
        db_flag_map = {
            '1': 'Military',
            '2': 'Interesting',
            '4': 'PIA',
            '8': 'LADD'
        }
        db_flag = flight.get('dbFlags', '')
        return db_flag_map.get(db_flag)
    
    def _map_emergency(self, flight: dict) -> Optional[str]:
        squawk_translation = {
            '7500': 'Hijacked Aircraft!',
            '7600': 'Radio Failure!',
            '7700': 'Emergency!'
        }
        emergency = flight.get('emergency') if flight.get('emergency') != 'none' else None
        squawk = flight.get('squawk', '')
        squawk_translated = squawk_translation.get(squawk)
        if squawk_translated and emergency:
            return f'{squawk_translated} {emergency}'
        return squawk_translated or emergency

    def _safe_cast_to_int(self, value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value is not None else None
        except ValueError as e:
            log.warning(f'Error casting scatter data to int: {e}')
            return None

    def _safe_cast_to_float(self, value: Optional[str]) -> Optional[float]:
        try:
            return float(value) if value is not None else None
        except ValueError as e:
            log.warning(f'Error casting scatter data to float: {e}')
            return None

    def _add_sample_date(
            self, flight_sample: Iterator[FlightSamples]) -> Iterator[FlightSamples]:
        '''
        Adds a sample collection date to each mapped row of the flight sample.
        '''
        log.info('adding sample date to mapped flight sample')
        sample_collection_date = datetime.utcnow().replace(tzinfo=pytz.utc)
        for table_row in flight_sample:
            table_row.sample_entry_date_utc = sample_collection_date
            yield table_row
        log.info('sample date added to mapped flight sample')
