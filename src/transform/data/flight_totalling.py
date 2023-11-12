from config.logger import Logger
from transform.data.base_calcs import BaseCalcs
from transform.db.repository import DbRepo
from database.models import FlightAggregates, DailyFlightTotals, WeeklyFlightTotals, MonthlyFlightTotals

from sqlalchemy.orm import Session
import polars as pl

from typing import Iterator
from datetime import datetime, timedelta

log = Logger.create(__name__)


class FlightTotaller(BaseCalcs):
    '''
    Populates flight totals tables for efficiently presenting historic trends.
    '''
    def __init__(self) -> None:
        self.db = DbRepo()

    def total_daily_aggregates(self):                                    # abstract this with FlightAggregator
        with Session(self.db.engine) as session:
            unmatched_aggregates: Iterator[FlightAggregates] = self.db.get_new_flight_aggregates(session)
        for agg_sample_date in unmatched_aggregates:
            sample_datetime: datetime = datetime.strptime(agg_sample_date[0], '%Y-%m-%d')
            query_end_date = sample_datetime + timedelta(days=1)
            daily_aggregates: pl.LazyFrame = self.db.filter_table_by_dates(
                FlightAggregates, FlightAggregates.sample_entry_date_utc, sample_datetime, query_end_date
                ).lazy()
            daily_flight_totals_row = self.summarize_aggregates(daily_aggregates)
            with Session(self.db.engine) as session, session.begin():
                session.add(daily_flight_totals_row)
            
    def summarize_aggregates(self, aggregates: pl.LazyFrame) -> DailyFlightTotals:
        total_row = DailyFlightTotals(
            sample_date = aggregates.select(pl.col(FlightAggregates.sample_entry_date_utc.name)).first().collect().item(),
        )

    def _add_daily_date_columns(
            self, daily_totals_row: DailyFlightTotals, sample_datetime: datetime) -> DailyFlightTotals:
        daily_totals_row.sample_date = sample_datetime.date()
        daily_totals_row.day_of_week = sample_datetime.year
        daily_totals_row.day_and_number = sample_datetime.month
        return daily_totals_row


    def aggregate_weekly_totals(self):
        pass

    def aggregate_monthly_totals(self):
        pass


FlightTotaller().total_daily_aggregates()