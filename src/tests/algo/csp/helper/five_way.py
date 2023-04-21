# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

import networkx as nx

from tests.algo.csp.helper.ways import Graph, Time, Ways


@dataclass
class FiveWay(Ways):
    """Static data class to stub a graph with one path that leads to a solution and four slower paths"""

    _graph = nx.DiGraph()
    _graph.add_node(1, COST=10)
    _graph.add_node(2, COST=20)
    _graph.add_node(3, COST=30)
    _graph.add_node(4, COST=40)
    _graph.add_node(5, COST=50)
    _graph.add_node(6, COST=60)
    _graph.add_edge(1, 3, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(1, 2, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(2, 3, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(1, 4, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(4, 3, ROAD_TIME=2, FUEL_TIME=2, BREAK_TIME=2)
    _graph.add_edge(1, 5, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(5, 3, ROAD_TIME=3, FUEL_TIME=3, BREAK_TIME=3)
    _graph.add_edge(1, 6, ROAD_TIME=1, FUEL_TIME=1, BREAK_TIME=1)
    _graph.add_edge(6, 3, ROAD_TIME=4, FUEL_TIME=4, BREAK_TIME=4)

    input_graph = _graph

    time = Time(arc_road_time_total=3, arc_time_total=3, arc_time=1, arc_road_time=1)

    sol = Graph(
        arc_road_time_total=([1, 3], time.arc_road_time_total),
        arc_time_total=([1, 3], time.arc_time_total),
        arc_time=([1, 3], time.arc_time),
        arc_road_time=([1, 3], time.arc_road_time),
    )
