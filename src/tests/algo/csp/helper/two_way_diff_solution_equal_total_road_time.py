# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import networkx as nx

from tests.algo.csp.helper.ways import Graph, Time, Ways


@dataclass
class TwoWayDiffSolutionEqualTotalRoadTime(Ways):
    """Static data class to stub a graph with two paths with equal total road time that lead to a solution and three
    possible solutions."""

    _graph = nx.DiGraph()
    _graph.add_node(1, COST=10)
    _graph.add_node(2, COST=20)
    _graph.add_node(3, COST=30)
    _graph.add_edge(1, 2, ROAD_TIME=1, FUEL_TIME=2, BREAK_TIME=2)
    _graph.add_edge(2, 3, ROAD_TIME=1, FUEL_TIME=2, BREAK_TIME=2)
    _graph.add_edge(1, 3, ROAD_TIME=8, FUEL_TIME=1, BREAK_TIME=1)

    input_graph = _graph

    time = Time(arc_road_time_total=10, arc_time_total=10, arc_time=8, arc_road_time=2)

    sol = Graph(
        arc_road_time_total=([1, 2, 3], time.arc_road_time_total),
        arc_time_total=([1, 3], time.arc_time_total),
        arc_time=([1, 2, 3], time.arc_road_time),
        arc_road_time=([1, 2, 3], time.arc_road_time),
    )
