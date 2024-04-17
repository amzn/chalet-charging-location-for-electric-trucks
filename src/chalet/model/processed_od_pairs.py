# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Processed od pairs."""
from chalet.model.input.od_pair import OdPair


class OdPairs:
    """Definition of processed od pairs."""

    origin_id = OdPair.origin_id
    destination_id = OdPair.destination_id
    demand = OdPair.demand
    distance = "DISTANCE"
    legs = "LEGS"
    max_time = "MAX_TIME"
    max_road_time = "MAX_ROAD_TIME"
    feasible = "FEASIBLE"
    covered = "COVERED"
    stations = "STATIONS"
    fuel_stops = "FUEL_STOPS"
    direct_distance = "DIRECT_DISTANCE"
    direct_time = "DIRECT_TIME"
    route_distance = "ROUTE_DISTANCE"
    route_time = "ROUTE_TIME"
