from database.models import FlightSamples, FlightAggregates

from sqlalchemy.orm import Session


def get_flight_samples(session: Session) -> list[FlightSamples]:
    '''
    Fetches flight samples without matching aggregates.

    select distinct sample_entry_date_utc
    from flight_samples
    left join flight_aggregates
    on flight_samples.sample_entry_date_utc = flight_aggregates.sample_entry_date_utc
    where flight_aggregates.sample_entry_date_utc is null
    '''
    session.query(FlightSamples.sample_entry_date_utc).distinct()
