from database.models import FlightSamples
from flights.utils import logger

from typing import Optional, Iterator

log = logger.create(__name__)


class FlightSamplesMapper:
    '''
    Takes the cleaned scatter data from ADSB exchange and maps it to the flight samples table model.
    '''
    def map_scatter_data(self, scatter_data: list[dict]) -> Iterator[FlightSamples]:
        log.info(f'mapping {len(scatter_data)} rows of scatter data to flight samples table model')
        filtered_flights = filter(self._filter_flight, scatter_data)
        flights = map(self._map_flight, filtered_flights)
        log.info('mapped scatter data to flight samples table model')
        return flights
    
    def _filter_flight(self, flight: dict) -> bool:
        valid_flight = bool(flight.get('alt_baro') != 'ground'
                            and flight.get('hex')
                            and flight.get('lat')
                            and flight.get('lon')
                            )
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
