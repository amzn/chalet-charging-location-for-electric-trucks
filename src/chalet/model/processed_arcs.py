# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Processed arcs."""
from chalet.model.input.arc import Arc


class Arcs:
    """Definition of processed arcs."""

    head_id = Arc.head_id
    tail_id = Arc.tail_id
    time = "ROAD_TIME"
    distance = Arc.distance
    fuel_time = "FUEL_TIME"
    break_time = "BREAK_TIME"
