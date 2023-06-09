from flights.config.settings import s
from flights.utils import logger
from flights.data.mappers. flights_model_map import FlightsMapper
from flights.api.clients.adsb_exchange import AdsbExchangeClient
from flights.db.base_repo import BaseRepository

from hydra.utils import instantiate

import asyncio
from datetime import datetime
import pytz

log = logger.create(__name__)


def app_routine(db: BaseRepository):
    sample_collection_date = datetime.utcnow().replace(tzinfo=pytz.utc)
    scatter_api_response = AdsbExchangeClient().get_aircraft_scatter(39.8564, -104.6764)  # take_sample()
    flights_rows = FlightsMapper().map_scatter_data(scatter_api_response, sample_collection_date)
    # dedupe()
    db.insert_rows(flights_rows)


async def main():
    log.info('starting flights app')
    db: BaseRepository = instantiate(s.db)
    db.upgrade_db()
    while True:
        if s.general.suppress_errors:
            try:
                app_routine(db)
                await asyncio.sleep(1)
            except Exception as e:
                log.error(e)
                await asyncio.sleep(60)
                log.info('restarting flights app')
        else:
            app_routine(db)
            await asyncio.sleep(1)


if __name__ == '__main__':
    # asyncio.run(main())
    db: BaseRepository = instantiate(s.db)
    db.upgrade_db()
    app_routine(db)
