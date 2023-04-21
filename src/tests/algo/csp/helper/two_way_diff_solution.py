# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import networkx as nx

from tests.algo.csp.helper.ways import EMPTY_GRAPH_SOLUTION, Cost, Graph, Time, Ways


@dataclass
class TwoWayDiffSolution(Ways):
    """Static data class to stub a graph with two paths that lead to a solution and four possible solutions."""

    _graph = nx.DiGraph()
    _graph.add_node(1, COST=10)
    _graph.add_node(2, COST=20)
    _graph.add_node(3, COST=30)
    _graph.add_node(4, COST=40)
    _graph.add_edge(1, 2, ROAD_TIME=2, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(2, 3, ROAD_TIME=2, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(1, 3, ROAD_TIME=1, FUEL_TIME=10, BREAK_TIME=10)

    input_graph = _graph

    time = Time(arc_road_time_total=21, arc_time_total=8, arc_time=4, arc_road_time=1)

    sol = Graph(
        arc_road_time_total=([1, 3], time.arc_road_time_total),
        arc_time_total=([1, 2, 3], time.arc_time_total),
        arc_time=([1, 2, 3], time.arc_time),
        arc_road_time=([1, 3], time.arc_road_time),
    )

    sol_cost = Cost(
        road_time_and_road_time_total=([1, 3], 30),
        time_and_road_time_total=([1, 3], 30),
        road_time_and_time_total=EMPTY_GRAPH_SOLUTION,
        time_and_time_total=([1, 2, 3], 50),
    )
