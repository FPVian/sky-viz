from skyviz.config.settings import s
from database.models import FlightAggregates
from skyviz.db.base_repo import BaseRepository

from sqlalchemy.orm import Session
from hydra.utils import instantiate


db: BaseRepository = instantiate(s.db)
with Session(db.engine) as session:
    minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightAggregates.sample_entry_date_utc)

print(minutes_since_last_update)