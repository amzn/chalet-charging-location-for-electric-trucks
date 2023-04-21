# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx

from tests.algo.csp.helper.ways import EMPTY_GRAPH_SOLUTION, INF_VALUE, Cost, Graph, Time, Ways


class InvalidWay(Ways):
    """Static data class to stub a graph with no paths and no edges"""

    input_graph = nx.DiGraph()

    time = Time(arc_road_time_total=INF_VALUE, arc_time_total=2, arc_time=1, arc_road_time=0)

    sol = Graph(
        arc_road_time_total=EMPTY_GRAPH_SOLUTION,
        arc_time_total=EMPTY_GRAPH_SOLUTION,
        arc_time=EMPTY_GRAPH_SOLUTION,
        arc_road_time=EMPTY_GRAPH_SOLUTION,
    )

    sol_cost = Cost(
        road_time_and_road_time_total=EMPTY_GRAPH_SOLUTION,
        time_and_road_time_total=EMPTY_GRAPH_SOLUTION,
        road_time_and_time_total=EMPTY_GRAPH_SOLUTION,
        time_and_time_total=EMPTY_GRAPH_SOLUTION,
    )
