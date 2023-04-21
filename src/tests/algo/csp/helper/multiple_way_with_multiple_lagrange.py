# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import networkx as nx

from tests.algo.csp.helper.ways import EMPTY_GRAPH_SOLUTION, Cost, Graph, Time, Ways


@dataclass
class MultipleWayWithMultipleLagrange(Ways):
    """Static data class to stub a graph with two paths that lead to a solution and four possible solutions. It uses
    the Lagrangian to optimize for both bounds."""

    _graph = nx.DiGraph()
    _graph.add_node(1, COST=10)
    _graph.add_node(2, COST=20)
    _graph.add_node(3, COST=30)
    _graph.add_node(4, COST=40)
    _graph.add_node(5, COST=50)
    _graph.add_node(6, COST=60)
    _graph.add_node(7, COST=60)
    _graph.add_edge(1, 2, ROAD_TIME=2, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(2, 3, ROAD_TIME=2, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(1, 3, ROAD_TIME=1, FUEL_TIME=10, BREAK_TIME=10)
    _graph.add_edge(1, 4, ROAD_TIME=1, FUEL_TIME=1.5, BREAK_TIME=1.5)
    _graph.add_edge(4, 3, ROAD_TIME=1, FUEL_TIME=1.5, BREAK_TIME=1.5)
    _graph.add_edge(1, 5, ROAD_TIME=0.75, FUEL_TIME=3, BREAK_TIME=3)
    _graph.add_edge(5, 3, ROAD_TIME=0.75, FUEL_TIME=3, BREAK_TIME=3)
    _graph.add_edge(1, 6, ROAD_TIME=0.5, FUEL_TIME=20, BREAK_TIME=20)
    _graph.add_edge(6, 3, ROAD_TIME=0, FUEL_TIME=0, BREAK_TIME=0)
    _graph.add_edge(1, 7, ROAD_TIME=0, FUEL_TIME=100, BREAK_TIME=100)
    _graph.add_edge(7, 3, ROAD_TIME=0, FUEL_TIME=100, BREAK_TIME=100)

    input_graph = _graph

    time = Time(arc_road_time_total=21, arc_time_total=8, arc_time=4, arc_road_time=1)

    sol = Graph(
        arc_road_time_total=([1, 3], time.arc_road_time_total),
        arc_time_total=([1, 2, 3], time.arc_time_total),
        arc_time=([1, 4, 3], 2),
        arc_road_time=([1, 3], time.arc_road_time),
    )

    sol_cost = Cost(
        road_time_and_road_time_total=([1, 3], 30),
        time_and_road_time_total=([1, 3], 30),
        road_time_and_time_total=EMPTY_GRAPH_SOLUTION,
        time_and_time_total=([1, 2, 3], 50),
    )
