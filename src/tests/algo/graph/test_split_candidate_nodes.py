# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx

from chalet.algo.graph import _split_candidate_nodes
from tests.algo.graph.graph_data import NODE_ATTR_COST_ONE, NODE_ATTR_COST_ZERO
from tests.networkx_testing.testing import assert_graph_equal


def test_single_path():
    """Test for split_candidate_nodes. Uses a single one directional path."""
    input_graph = nx.DiGraph()
    input_graph.add_nodes_from([1, 2, 3, 4, 5], **NODE_ATTR_COST_ONE)
    nx.add_path(input_graph, [1, 2, 3, 4, 5])
    expected = nx.DiGraph()
    expected.add_nodes_from([1, 2, 3, 4, 5], **NODE_ATTR_COST_ONE)
    expected.add_nodes_from([-2, -3, -4], **NODE_ATTR_COST_ZERO)
    nx.add_path(expected, [1, 2, -2, 3, -3, 4, -4, 5])

    actual = _split_candidate_nodes(input_graph)

    assert_graph_equal(actual, expected)


def test_two_paths_with_cross_link():
    """Test for split_candidate_nodes. Uses two paths with cross link."""
    input_graph = nx.DiGraph()
    input_graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], **NODE_ATTR_COST_ONE)
    nx.add_path(input_graph, [1, 2, 3, 4, 8])
    nx.add_path(input_graph, [1, 5, 6, 7, 8])
    nx.add_path(input_graph, [3, 9, 10, 6])
    expected = nx.DiGraph()
    expected.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], **NODE_ATTR_COST_ONE)
    expected.add_nodes_from([-2, -3, -4, -5, -6, -7, -9, -10], **NODE_ATTR_COST_ZERO)
    nx.add_path(expected, [1, 2, -2, 3, -3, 4, -4, 8])
    nx.add_path(expected, [1, 5, -5, 6, -6, 7, -7, 8])
    nx.add_path(expected, [-3, 9, -9, 10, -10, 6])

    actual = _split_candidate_nodes(input_graph)

    assert_graph_equal(actual, expected)


def test_zero_cost_path():
    """Test for split_candidate_nodes. Uses a single one directional path with zero cost."""
    input_graph = nx.DiGraph()
    input_graph.add_nodes_from([1, 2, 3, 4, 5], **NODE_ATTR_COST_ZERO)
    nx.add_path(input_graph, [1, 2, 3, 4, 5])
    expected = input_graph.copy()

    actual = _split_candidate_nodes(input_graph)

    assert_graph_equal(actual, expected)


def test_empty_graph():
    """Test for split_candidate_nodes. Uses an empty graph."""
    input_graph = nx.DiGraph()
    expected = nx.DiGraph()

    actual = _split_candidate_nodes(input_graph)

    assert_graph_equal(actual, expected)
