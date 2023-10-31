from database.models import FlightAggregates
from skyviz.db.repository import DbRepo

from sqlalchemy.orm import Session


db = DbRepo()
with Session(db.engine) as session:
    minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightAggregates.sample_entry_date_utc)

print(minutes_since_last_update)
