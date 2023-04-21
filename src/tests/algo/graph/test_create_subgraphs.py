# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict

import networkx as nx

from chalet.algo.graph import create_subgraphs
from chalet.model.input.node import Node
from chalet.model.processed_arcs import Arcs
from tests.algo.graph.graph_data import get_stub_arcs, get_stub_nodes, get_stub_od_pairs, get_stub_time_dist_map
from tests.networkx_testing.testing import assert_graphs_equal


def test_create_subgraphs():
    """Test for create_subgraphs."""

    def make_edge_attr(time: float) -> Dict[str, float]:
        return {Arcs.time: time, Arcs.fuel_time: 0.0, Arcs.break_time: 0.0, Arcs.distance: time}

    graph1 = nx.DiGraph()
    graph1.add_nodes_from([1, 2], **{Node.cost: 1.0})
    graph1.add_edge(1, 2, **make_edge_attr(10.0))
    graph2 = nx.DiGraph()
    graph2.add_nodes_from([2, 3], **{Node.cost: 1.0})
    graph2.add_edge(2, 3, **make_edge_attr(40.0))
    graph3 = nx.DiGraph()
    graph3.add_nodes_from([3, 4], **{Node.cost: 1.0})
    graph3.add_edge(3, 4, **make_edge_attr(60.0))
    expected = [graph1, graph2, graph3]

    actual = create_subgraphs(
        get_stub_od_pairs(),
        get_stub_arcs(),
        get_stub_nodes(),
        get_stub_time_dist_map(),
        truck_range=300,
        fuel_time_bound=75,
        num_proc=1,
    )

    assert_graphs_equal(actual, expected)
