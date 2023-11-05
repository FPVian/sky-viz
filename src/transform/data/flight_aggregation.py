from config.logger import Logger
from database.models import FlightSamples, FlightAggregates
from transform.db.repository import DbRepo
from transform.data.base_calcs import BaseCalcs

from sqlalchemy.orm import Session
import polars as pl

from typing import Iterator
from datetime import datetime

log = Logger.create(__name__)


class FlightAggregator(BaseCalcs):
    '''
    Populates flight_aggregates table for efficiently querying flight data.
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
        Summarizes a sample of flights into a single row of the flight_aggregates table.
        '''
        sample_date = flight_sample.select(
            pl.col(FlightSamples.sample_entry_date_utc.name)).first().collect().item()
        log.info(f'summarizing flight sample from: {sample_date}')
        agg_row = FlightAggregates()
        agg_row.sample_entry_date_utc = sample_date
        agg_row.number_of_flights = flight_sample.select(pl.count()).collect().item()
        agg_row.avg_altitude_ft = flight_sample.select(
            pl.col(FlightSamples.altitude_ft.name)).mean().collect().item()
        agg_row = self._calculate_max_altitude_columns(flight_sample, agg_row)
        agg_row = self._calculate_max_climb_columns(flight_sample, agg_row)
        agg_row = self._calculate_max_descent_columns(flight_sample, agg_row)
        agg_row.avg_ground_speed_knots = flight_sample.select(
            pl.col(FlightSamples.ground_speed_knots.name)).mean().collect().item()
        agg_row = self._calculate_max_speed_columns(flight_sample, agg_row)
        log.info(f'returning summarized sample as flight_aggregates row for: {sample_date}')
        return agg_row
    
    def _calculate_max_altitude_columns(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        '''
        Calculates the max altitude and associated aircraft type, registration, and flight
        for a sample of flights.
        '''
        log.info('calculating max altitude flight for sample')
        max_alt_row = self._filter_to_max_row(flight_sample, FlightSamples.altitude_ft)
        if max_alt_row.height == 1:
            agg_row.max_altitude_ft = max_alt_row.select(pl.col(FlightSamples.altitude_ft.name)).item()
            agg_row.max_alt_aircraft_type = max_alt_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_alt_aircraft_registration = max_alt_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_alt_flight = max_alt_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning('no max altitude for sample; all values are null')
        log.info('returning max altitude flight for sample')
        return agg_row

    def _calculate_max_climb_columns(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        '''
        Calculates the max climb rate and associated aircraft type, registration, and flight
        for a sample of flights.
        '''
        log.info('calculating max climb rate flight for sample')
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
            log.warning('no max climb rate for sample; all values are <= 0 or null')
        log.info('returning max climb rate flight for sample')
        return agg_row
    
    def _calculate_max_descent_columns(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        '''
        Calculates the max descent rate and associated aircraft type, registration, and flight
        for a sample of flights.
        '''
        log.info('calculating max descent rate flight for sample')
        descent_rows = flight_sample.filter(pl.col(FlightSamples.alt_change_ft_per_min.name) < 0)
        max_descent_row = self._filter_to_min_row(descent_rows, FlightSamples.alt_change_ft_per_min)
        if max_descent_row.height == 1:
            descent_rate = max_descent_row.select(
                pl.col(FlightSamples.alt_change_ft_per_min.name)).item()
            agg_row.max_descent_rate_ft_per_min = -1 * descent_rate
            agg_row.max_descent_aircraft_type = max_descent_row.select(
                pl.col(FlightSamples.aircraft_type.name)).item()
            agg_row.max_descent_aircraft_registration = max_descent_row.select(
                pl.col(FlightSamples.aircraft_registration.name)).item()
            agg_row.max_descent_flight = max_descent_row.select(pl.col(FlightSamples.flight.name)).item()
        else:
            log.warning('no max descent rate for sample; all values are >= 0 or null')
        log.info('returning max descent rate flight for sample')
        return agg_row
    
    def _calculate_max_speed_columns(
            self, flight_sample: pl.LazyFrame, agg_row: FlightAggregates) -> FlightAggregates:
        '''
        Calculates the max speed and associated aircraft type, registration, and flight
        for a sample of flights.
        '''
        log.info('calculating max speed flight for sample')
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
            log.warning('no max speed value for sample; all values are null')
        log.info('returning max speed flight for sample')
        return agg_row
