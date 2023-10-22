from database.models import FlightAggregates

from sqlalchemy.orm import Session
from hydra.utils import instantiate

import os

os.environ['SKYVIZ_ENV'] = 'prod'
from skyviz.config.settings import s

db = instantiate(s.db)
with Session(db.engine) as session, session.begin():
    minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightAggregates.sample_entry_date_utc)

print(minutes_since_last_update)