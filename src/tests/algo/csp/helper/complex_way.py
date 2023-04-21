# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import networkx as nx

from tests.algo.csp.helper.ways import Cost, Graph, Time, Ways


@dataclass
class ComplexWay(Ways):
    """Static data class to stub a complex graph. A complex graph is defined as a graph that does not test for a
    specific case but a group of possible edge cases."""

    _graph = nx.DiGraph()
    _graph.add_node(1, COST=10)
    _graph.add_node(2, COST=20)
    _graph.add_node(3, COST=30)
    _graph.add_node(4, COST=40)
    _graph.add_node(5, COST=50)
    _graph.add_node(6, COST=60)
    _graph.add_node(7, COST=70)
    _graph.add_node(8, COST=80)
    _graph.add_edge(1, 2, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(2, 4, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(4, 5, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(5, 3, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(1, 4, ROAD_TIME=2, FUEL_TIME=2, BREAK_TIME=2)
    _graph.add_edge(1, 5, ROAD_TIME=3, FUEL_TIME=3, BREAK_TIME=3)
    _graph.add_edge(1, 6, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(6, 7, ROAD_TIME=10, FUEL_TIME=10, BREAK_TIME=10)
    _graph.add_edge(1, 8, ROAD_TIME=10, FUEL_TIME=10, BREAK_TIME=10)
    _graph.add_edge(8, 3, ROAD_TIME=10, FUEL_TIME=10, BREAK_TIME=10)

    input_graph = _graph

    time = Time(arc_road_time_total=12, arc_time_total=12, arc_time=4, arc_road_time=4)

    sol = Graph(
        arc_road_time_total=([1, 5, 3], time.arc_road_time_total),
        arc_time_total=([1, 5, 3], time.arc_time_total),
        arc_time=([1, 5, 3], time.arc_time),
        arc_road_time=([1, 5, 3], time.arc_road_time),
    )

    sol_cost = Cost(
        road_time_and_road_time_total=([1, 5, 3], 80),
        time_and_road_time_total=([1, 5, 3], 80),
        road_time_and_time_total=([1, 5, 3], 80),
        time_and_time_total=([1, 5, 3], 80),
    )
