# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from collections import namedtuple
from dataclasses import dataclass
from typing import List, Tuple

import networkx as nx

INF_VALUE: float = float("inf")
EMPTY_GRAPH_SOLUTION: Tuple[List[int], float] = ([], INF_VALUE)

Cost = namedtuple(
    "Cost",
    [
        "road_time_and_road_time_total",
        "time_and_road_time_total",
        "road_time_and_time_total",
        "time_and_time_total",
    ],
)
Time = namedtuple("Time", ["arc_road_time_total", "arc_time_total", "arc_time", "arc_road_time"])
Graph = namedtuple("Graph", ["arc_road_time_total", "arc_time_total", "arc_time", "arc_road_time"])


@dataclass
class Ways(ABC):
    """Abstract data class to stub graph and expected solutions."""

    input_graph: nx.DiGraph
    time: Time
    sol: Graph
    sol_cost: Cost
