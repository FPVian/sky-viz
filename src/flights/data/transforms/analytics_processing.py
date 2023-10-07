from flights.utils import logger
from database.models import FlightSamples, FlightAggregates

from sqlalchemy import select
from sqlalchemy.orm import Session

log = logger.create(__name__)


def get_flight_samples(session: Session) -> list[FlightSamples]:
    '''
    Fetches flight samples without matching aggregates.

    select distinct sample_entry_date_utc
    from flight_samples
    left join flight_aggregates
    on flight_samples.sample_entry_date_utc = flight_aggregates.sample_entry_date_utc
    where flight_aggregates.sample_entry_date_utc is null
    '''
    log.info('fetching flight samples that need to be aggregated')
    sql_query = select(FlightSamples.sample_entry_date_utc).distinct()
    sample_dates = session.execute(sql_query)
    log.info(f'summarizing {len(sample_dates)} rows from flight_samples table')
