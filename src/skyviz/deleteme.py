from skyviz.config.settings import s
from database.models import FlightSamples
from skyviz.db.base_repo import BaseRepository

from hydra.utils import instantiate


db: BaseRepository = instantiate(s.db)
print(db.read_table(FlightSamples))
