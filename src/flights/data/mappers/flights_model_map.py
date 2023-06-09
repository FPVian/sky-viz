from flights.db.model import Flights
from flights.utils import logger

from datetime import datetime
from typing import Optional

log = logger.create(__name__)


class FlightsMapper:
    '''
    Takes the scatter data from the ADSB exchange API and maps it to the flights db model.
    '''

    def map_scatter_data(self, scatter_data: list[dict], sample_entry_date: datetime) -> list[Flights]:
        log.info(f'mapping {len(scatter_data)} rows of scatter data to flights table model')
        flights = []
        for flight in scatter_data:
            if flight.get('alt_baro') != 'ground' and flight.get('hex') and flight.get('lat') and flight.get('lon'):
                table_row = Flights()
                table_row.flight = flight.get('flight')
                table_row.latitude = self._safe_cast_to_float(flight['lat'])
                table_row.longitude = self._safe_cast_to_float(flight['lon'])
                table_row.altitude_ft = self._safe_cast_to_int(flight.get('alt_baro'))

                table_row.alt_change_ft_per_min = self._safe_cast_to_int(flight.get('baro_rate'))
                if table_row.alt_change_ft_per_min is None:
                    table_row.alt_change_ft_per_min = self._safe_cast_to_int(flight.get('geom_rate'))

                table_row.heading = self._safe_cast_to_float(flight.get('track'))
                table_row.ground_speed_knots = self._safe_cast_to_float(flight.get('gs'))
                table_row.nav_modes = flight.get('nav_modes')
                table_row.emitter_category = flight.get('category')
                table_row.aircraft_type = flight.get('t')
                table_row.aircraft_registration = flight.get('r')
                table_row.flag = self._map_dbflags(flight)
                table_row.source = flight.get('type')
                table_row.rssi = self._safe_cast_to_float(flight.get('rssi'))
                table_row.emergency = self._map_emergency(flight)
                table_row.sample_entry_date_utc = sample_entry_date
                table_row.icao_id = flight['hex']

                flights.append(table_row)
        log.info(f'mapped {len(flights)} rows of scatter data to flights table model')
        return flights
    
    def _map_dbflags(self, flight: dict) -> Optional[str]:
        dbflag = flight.get('dbFlags')
        if dbflag == '1':
            return 'Military'
        elif dbflag == '2':
            return 'Interesting'
        elif dbflag == '4':
            return 'PIA'
        elif dbflag == '8':
            return 'LADD'
        else:
            return None
    
    def _map_emergency(self, flight: dict) -> Optional[str]:
        emergency = flight.get('emergency') if flight.get('emergency') != 'none' else None
        squawk = flight.get('squawk')
        if squawk == '7500':
            squawk_translated = 'Hijacked Aircraft!'
        elif squawk == '7600':
            squawk_translated = 'Radio Failure!'
        elif squawk == '7700':
            squawk_translated = 'Emergency!'
        else:
            return emergency
        return f'{squawk_translated} {emergency}' if emergency is not None else squawk_translated

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
