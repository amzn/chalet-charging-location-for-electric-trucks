# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx
from pandas.testing import assert_frame_equal

from chalet.model.processed_od_pairs import OdPairs
from chalet.preprocess.od_pairs_helpers import generate_subgraphs_for_od_pairs
from tests.networkx_testing.testing import assert_graphs_equal
from tests.preprocess.stub_data import (
    FUEL_TIME_BOUND,
    NUM_PROC,
    get_stub_arcs,
    get_stub_nodes,
    get_stub_parameters,
    get_stub_processed_od_pairs,
    get_stub_time_dist_map,
)


def test_generate_subgraphs_for_od_pairs():
    """Test for generate_subgraphs_for_od_pairs"""
    parameters = get_stub_parameters()
    actual_od_pairs = get_stub_processed_od_pairs()
    expected_od_pairs = get_stub_processed_od_pairs()
    expected_od_pairs[OdPairs.feasible] = True
    arcs = get_stub_arcs()
    nodes = get_stub_nodes()
    time_dist_map = get_stub_time_dist_map()
    graph1 = nx.DiGraph()
    graph1.add_edge(1, 2)
    graph2 = nx.DiGraph()
    graph2.add_edge(2, 3)
    graph3 = nx.DiGraph()
    graph3.add_edge(3, 4)
    expected_subgraphs = [graph1, graph2, graph3]

    actual_subgraphs = generate_subgraphs_for_od_pairs(
        parameters,
        actual_od_pairs,
        arcs,
        nodes,
        time_dist_map,
        FUEL_TIME_BOUND,
        NUM_PROC,
    )

    assert_frame_equal(actual_od_pairs, expected_od_pairs)
    assert_graphs_equal(actual_subgraphs, expected_subgraphs, node_data=False, edge_data=False)
