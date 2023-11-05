from config.logger import Logger
from database.models import FlightSamples, FlightAggregates
from transform.db.repository import DbRepo

from sqlalchemy.orm import Session, Mapped
import polars as pl

from typing import Iterator
from datetime import datetime, date, timedelta

log = Logger.create(__name__)


class FlightsProcessor:
    '''
    Populates tables for running analytics on flight data.
    '''
    def __init__(self) -> None:
        self.db = DbRepo()

    def aggregate_flight_samples(self) -> None:
        '''
        Gets new flight samples, summarizes them, and inserts them into the flight_aggregates table.
        '''
        log.info('summarizing flight samples')
        with Session(self.db.engine) as session:
            unmatched_flight_samples: Iterator[FlightSamples] = self.db.get_new_flight_samples(session)  # need to sort rows by date?
        for flight_sample_date in unmatched_flight_samples:  # delete any dependent daily, weekly, monthly totals
            sample_date: datetime = flight_sample_date.sample_entry_date_utc
            flight_sample: pl.LazyFrame = self.db.filter_table_by_dates(
                FlightSamples, FlightSamples.sample_entry_date_utc, sample_date
                ).lazy()
            aggregate_row = self.summarize_flight_sample(flight_sample)
            with Session(self.db.engine) as session, session.begin():
                session.add(aggregate_row)
        log.info('summarized flight samples')

    def summarize_flight_sample(self, flight_sample: pl.LazyFrame) -> FlightAggregates:
        '''
        Summarizes a sample of flight into a single row of the flight_aggregates table.
        '''
        sample_date = flight_sample.select(
            pl.col(FlightSamples.sample_entry_date_utc.name)).first().collect().item()
        log.info(f'summarizing flight sample from: {sample_date}')
        agg_row = FlightAggregates()
        agg_row.sample_entry_date_utc = sample_date
        agg_row.number_of_flights = flight_sample.select(pl.count()).collect().item()
        # Calculate average columns
        agg_row.avg_altitude_ft = flight_sample.select(
            pl.col(FlightSamples.altitude_ft.name)).mean().collect().item()
        agg_row.avg_ground_speed_knots = flight_sample.select(
            pl.col(FlightSamples.ground_speed_knots.name)).mean().collect().item()
        # Calculate max altitude columns
        max_alt_row = self._filter_to_max_row(flight_sample, FlightSamples.altitude_ft)
        if max_alt_row.height == 1:
            agg_row.max_altitude_ft = max_alt_row.select(pl.col(FlightSamples.altitude_ft.name)).item()
            agg_row.max_alt_aircraft_type = max_alt_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_alt_aircraft_registration = max_alt_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_alt_flight = max_alt_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning(f'no max altitude for sample: {sample_date}, all values are null')
        # Calculate max climb rate columns
        climb_rows = flight_sample.filter(pl.col(FlightSamples.alt_change_ft_per_min.name) > 0)
        max_climb_row = self._filter_to_max_row(climb_rows, FlightSamples.alt_change_ft_per_min)
        if max_climb_row.height == 1:
            agg_row.max_climb_rate_ft_per_min = max_climb_row.select(
                pl.col(FlightSamples.alt_change_ft_per_min.name)).item()
            agg_row.max_climb_aircraft_type = max_climb_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_climb_aircraft_registration = max_climb_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_climb_flight = max_climb_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning(f'no max climb rate for sample: {sample_date}, all values are <= 0 or null')
        # Calculate max descent rate columns
        descent_rows = flight_sample.filter(pl.col(FlightSamples.alt_change_ft_per_min.name) < 0)
        max_descent_row = self._filter_to_min_row(descent_rows, FlightSamples.alt_change_ft_per_min)
        if max_descent_row.height == 1:
            agg_row.max_descent_rate_ft_per_min = -1 * max_descent_row.select(
                pl.col(FlightSamples.alt_change_ft_per_min.name)).item()
            agg_row.max_descent_aircraft_type = max_descent_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_descent_aircraft_registration = max_descent_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_descent_flight = max_descent_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning(f'no max descent rate for sample: {sample_date}, all values are >= 0 or null')
        # Calculate max ground speed
        max_speed_row = self._filter_to_max_row(flight_sample, FlightSamples.ground_speed_knots)
        if max_speed_row.height == 1:
            agg_row.max_ground_speed_knots = max_speed_row.select(
                pl.col(FlightSamples.ground_speed_knots.name)).item()
            agg_row.max_speed_aircraft_type = max_speed_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_speed_aircraft_registration = max_speed_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_speed_flight = max_speed_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning(f'no max speed value for sample: {sample_date}, all values are null')
        log.info(f'returning summarized sample as flight_aggregates row for: {sample_date}')
        return agg_row


    def _filter_to_max_row(self, lazyframe: pl.LazyFrame, column: Mapped) -> pl.DataFrame:
        '''
        Filters a lazyframe to a single row based with the the max value in a given column.
        '''
        log.info(f'filtering to row with max value in column: {column.name}')
        max_row = lazyframe.lazy().filter(pl.col(column.name) == pl.max(column.name)).first().collect()
        log.info(f'returning row with max value in column: {column.name}')
        return max_row

    def _filter_to_min_row(self, lazyframe: pl.LazyFrame, column: Mapped) -> pl.DataFrame:
        '''
        Filters a lazyframe to a single row based with the the min value in a given column.
        '''
        log.info(f'filtering to row with min value in column: {column.name}')
        max_row = lazyframe.lazy().filter(pl.col(column.name) == pl.min(column.name)).first().collect()
        log.info(f'returning row with min value in column: {column.name}')
        return max_row


    '''
    Control flow:

    find sample dates with no matching daily aggregates
        if missing daily aggregates:
            summarize_daily_top_flights()

    find sample dates with no matching weekly aggregates
        if missing weekly aggregates:
            summarize_weekly_monthly_top_flights()

    find sample dates with no matching monthly aggregates
        if missing monthly aggregates:
            summarize_weekly_monthly_top_flights()
            count_flights_per_month()
    '''

    def summarize_daily_top_flights(self, entry_date: date) -> None:
        end_date = entry_date + timedelta(days=1)
        '''
        date = date
        avg_count_aircraft_type_per_sample()
        join 
        count_num_flights_by_aircraft_type()
        join
        count_unique_aircraft_by_aircraft_type
        insert into db
        '''
    
    def summarize_weekly_monthly_top_flights(self, start_date: datetime, end_date: datetime) -> None:
        pass
        '''
        date = date
        avg_count_aircraft_type_per_sample()
        join 
        !!! write function to sum daily totals
        join
        count_unique_aircraft_by_aircraft_type
        insert into db
        '''