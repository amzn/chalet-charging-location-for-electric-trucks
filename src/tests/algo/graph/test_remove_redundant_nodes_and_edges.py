# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx

from chalet.algo.graph import _remove_redundant_nodes_and_edges
from tests.algo.graph.graph_data import EDGE_ATTR_ALL_TIMES_ONE
from tests.networkx_testing.testing import assert_graph_equal

INF_VALUE = float("inf")


def make_complete_graph_with_attr(size: int) -> nx.DiGraph:
    """Test for remove_redundant_nodes_and_edges.
    Uses a max_time bound and an infinite time max_road_time bound."""
    graph = nx.DiGraph()
    edges = []
    for i in range(size):
        for j in range(size):
            edges.append((i, j))
    graph.add_edges_from(edges, **EDGE_ATTR_ALL_TIMES_ONE)
    return graph


def test_max_time_boundary():
    """Test for remove_redundant_nodes_and_edges.
    Uses a max_time bound and an infinite time max_road_time bound."""
    input_graph = nx.DiGraph()
    nx.add_path(input_graph, [1, 2], **EDGE_ATTR_ALL_TIMES_ONE)
    expected_left = nx.DiGraph()
    expected_right = input_graph.copy()

    actual_left = _remove_redundant_nodes_and_edges(input_graph, orig=1, dest=2, max_road_time=INF_VALUE, max_time=2)
    actual_right = _remove_redundant_nodes_and_edges(input_graph, orig=1, dest=2, max_road_time=INF_VALUE, max_time=3)

    assert_graph_equal(actual_left, expected_left)
    assert_graph_equal(actual_right, expected_right)


def test_max_road_time_boundary():
    """Test for remove_redundant_nodes_and_edges.
    Uses a max_time bound and an infinite time max_road_time bound."""
    input_graph = nx.DiGraph()
    nx.add_path(input_graph, [1, 2], **EDGE_ATTR_ALL_TIMES_ONE)
    expected_left = nx.DiGraph()
    expected_right = input_graph.copy()

    actual_left = _remove_redundant_nodes_and_edges(input_graph, orig=1, dest=2, max_road_time=0, max_time=INF_VALUE)
    actual_right = _remove_redundant_nodes_and_edges(input_graph, orig=1, dest=2, max_road_time=1, max_time=INF_VALUE)

    assert_graph_equal(actual_left, expected_left)
    assert_graph_equal(actual_right, expected_right)


def test_complete_graph_with_boundary():
    """Test for remove_redundant_nodes_and_edges.
    Uses a max_road_time bound and an infinite time max_time bound."""
    input_graph = make_complete_graph_with_attr(4)
    expected = nx.DiGraph()
    expected.add_edges_from([(0, 3)], **EDGE_ATTR_ALL_TIMES_ONE)
    expected.add_nodes_from([1, 2])

    actual = _remove_redundant_nodes_and_edges(input_graph, orig=0, dest=3, max_road_time=3, max_time=INF_VALUE)

    assert_graph_equal(actual, expected)


def test_path_out_of_boundaries():
    """Test for remove_redundant_nodes_and_edges. Uses a zero max_time and zero max_road_time boundary."""
    input_graph = nx.DiGraph()
    nx.add_path(input_graph, [1, 2], **EDGE_ATTR_ALL_TIMES_ONE)
    expected = nx.DiGraph()

    actual = _remove_redundant_nodes_and_edges(input_graph, orig=1, dest=2, max_road_time=0, max_time=0)

    assert_graph_equal(actual, expected)
