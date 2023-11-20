# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Preprocess arcs."""
import logging
import time

import pandas as pd

from chalet.common.battery_util import recharge_time
from chalet.common.constants import ROUND_OFF_FACTOR, TIME_DISTANCE_MAP, TRANSIT_TIME_KEY
from chalet.model.hash_map import Hashmap
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.node_type import NodeType
from chalet.model.parameters import Parameters
from chalet.model.processed_arcs import Arcs
from chalet.model.transit_time import TransitTime
from chalet.preprocess.preprocess import PreprocessData

logger = logging.getLogger(__name__)


class PreprocessArcs(PreprocessData):
    """Pre-processing of arcs."""

    def preprocess(self, data: dict):
        """Add self-loops, create time distance map and preprocess arcs."""
        nodes = data[Node.get_file_name()]
        arcs: pd.DataFrame = data[Arc.get_file_name()]
        logger.info(f"Processing: {len(arcs)} arcs.")

        # add self loops with trivial values for soundness of lookup map
        self_loops = pd.DataFrame(
            data=list(
                zip(
                    nodes[Node.id],
                    nodes[Node.id],
                    [0.0] * len(nodes),
                    [0.0] * len(nodes),
                )
            ),
            columns=arcs.columns,
        )
        arcs = pd.concat([arcs, self_loops], ignore_index=True)

        arcs = self._node_filter_arcs(arcs, nodes)

        # Add time-distance map in data
        data[TIME_DISTANCE_MAP] = self._create_time_distance_map(arcs)

        # start preprocessing of arcs
        data[Arc.get_file_name()] = self._preprocess_arcs(
            arcs, nodes, data[TRANSIT_TIME_KEY], data[Parameters.get_file_name()]
        )

    def _preprocess_arcs(
        self,
        arcs: pd.DataFrame,
        nodes: pd.DataFrame,
        transit_time_provider: TransitTime,
        params: Parameters,
    ) -> pd.DataFrame:
        """Filter arcs based on range, time and public/on-site station access.

        Add fuel time, break time and loading time attributes.
        """
        arcs.rename(columns={Arc.time: Arcs.time}, inplace=True)
        self._range_filter_arcs(
            arcs,
            nodes,
            params.orig_range,
            params.dest_range,
            params.safe_range,
            0.2 * params.safe_range,
        )
        self._add_fuel_time(arcs, nodes, params)  # adds column "FUEL_TIME"
        self._time_filter_arcs(arcs, nodes, params.min_fuel_time, params.max_fuel_time)  # needs column "FUEL_TIME"
        arcs[Arcs.break_time] = transit_time_provider.break_time(arcs[Arcs.time])  # adds column "BREAK_TIME"

        return arcs


    @staticmethod
    def _node_filter_arcs(
        arcs: pd.DataFrame,
        nodes: pd.DataFrame,
    ):
        """Removes all arcs whose endpoints are not contained in the provided nodes."""
        tail_exists = arcs[Arc.tail_id].isin(nodes[Node.id])
        head_exists = arcs[Arc.head_id].isin(nodes[Node.id])
        arcs = arcs.loc[tail_exists & head_exists].copy()

        return arcs


    @staticmethod
    def _range_filter_arcs(
        arcs: pd.DataFrame,
        nodes: pd.DataFrame,
        orig_range: float,
        dest_range: float,
        truck_range: float,
        min_dist: float = 0,
    ):
        """Filter the arcs according to range.

        Remove the arcs outgoing from sites if distance > orig_range.
        Remove the arcs incoming to sites if distance > truck_range - dest_range.
        Remove the arcs between stations if distance > truck_range.
        Remove the arcs between stations if distance < min_dist (default 0).
        Remove all arcs between sites (no direct routes).
        Remove all self-loops.
        """
        logger.info("Filtering arcs globally based on range..")
        start = time.time()

        values = [min_dist, orig_range, dest_range]
        for value in values:
            if value > truck_range:
                raise ValueError(f"{value} exceeds maximum truck range")

        tail_is_site = (nodes.loc[arcs[Arc.tail_id], Node.type] == NodeType.SITE).values
        head_is_site = (nodes.loc[arcs[Arc.head_id], Node.type] == NodeType.SITE).values
        exceeds_range = (arcs[Arc.distance] > truck_range).values
        exceeds_initial_range = (arcs[Arc.distance] > orig_range).values
        final_range = truck_range - dest_range
        exceeds_final_range = (arcs[Arc.distance] > final_range).values
        self_loop = arcs[Arc.tail_id] == arcs[Arc.head_id]
        too_close = (arcs[Arc.distance] < min_dist).values

        remove = (
            self_loop
            | exceeds_range
            | (head_is_site & exceeds_final_range)
            | (tail_is_site & exceeds_initial_range)
            | (tail_is_site & head_is_site)
            | (~tail_is_site & ~head_is_site & too_close)
        )
        arcs.drop(arcs[remove].index, inplace=True)

        end = time.time()
        logger.info(f"Finished in {round(end - start, ROUND_OFF_FACTOR)} secs. Arcs remaining: {len(arcs)}")

    @staticmethod
    def _add_fuel_time(arcs: pd.DataFrame, nodes: pd.DataFrame, params: Parameters):
        """Add refueling time as a separate attribute to arcs according to "charge enough" and destination range policy.

        Station to station: Add time to cover distance only.
        Station to site: Add time to cover distance plus dest_range.
        Site to station: Add nothing.
        Operations are performed in-place.
        """
        logger.info("Adding refueling time to arcs globally..")
        start = time.time()

        truck_range = params.truck_range
        buffer = params.min_state

        charger_power = params.charger_power
        battery_capacity = params.battery_capacity
        dest_range = params.dest_range

        tail_is_station = (nodes.loc[arcs[Arc.tail_id], Node.type] == NodeType.STATION).values
        head_is_site = (nodes.loc[arcs[Arc.head_id], Node.type] == NodeType.SITE).values

        arcs[Arcs.fuel_time] = 0

        def charge_time_to_station(dist):
            return recharge_time(buffer, buffer + dist / truck_range, charger_power, battery_capacity)

        def charge_time_to_site(dist):
            return recharge_time(
                buffer,
                buffer + (dist + dest_range) / truck_range,
                charger_power,
                battery_capacity,
            )

        arcs.loc[tail_is_station & ~head_is_site, Arcs.fuel_time] += arcs.loc[
            tail_is_station & ~head_is_site, Arc.distance
        ].apply(charge_time_to_station)
        arcs.loc[tail_is_station & head_is_site, Arcs.fuel_time] += arcs.loc[
            tail_is_station & head_is_site, Arc.distance
        ].apply(charge_time_to_site)

        end = time.time()
        logger.info(f"Finished in {round(end - start, ROUND_OFF_FACTOR)} secs.")

    @staticmethod
    def _time_filter_arcs(
        arcs: pd.DataFrame,
        nodes: pd.DataFrame,
        min_fuel_time: float,
        max_fuel_time: float,
    ):
        """Filter arcs based on refueling time bounds."""
        logger.info("Filtering arcs globally based on time..")
        tail_is_station = (nodes.loc[arcs[Arc.tail_id], Node.type] == NodeType.STATION).values
        fuel_time_too_low = (arcs[Arcs.fuel_time] < min_fuel_time).values
        fuel_time_too_high = (arcs[Arcs.fuel_time] > max_fuel_time).values
        remove = (fuel_time_too_low | fuel_time_too_high) & tail_is_station
        arcs.drop(arcs[remove].index, inplace=True)
        logger.info(f"Arcs remaining: {len(arcs)}")

    @staticmethod
    def _create_time_distance_map(arcs: pd.DataFrame) -> Hashmap:
        logger.info("Creating vectorized lookup map for time and distance values..")
        start = time.time()
        key_type = (
            arcs[[Arc.tail_id, Arc.head_id]].values.dtype,
            2,
        )  # array of length 2
        value_type = (arcs[[Arc.time, Arc.distance]].values.dtype, 2)
        time_dist_map = Hashmap(
            arcs[[Arc.tail_id, Arc.head_id]].values,
            arcs[[Arc.time, Arc.distance]].values,
            key_type,
            value_type,
            [float("inf"), float("inf")],
        )
        logger.info(f"Finished creating time distance map in {round(time.time() - start, ROUND_OFF_FACTOR)} secs.")
        return time_dist_map
