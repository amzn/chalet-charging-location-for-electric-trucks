# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, List

import networkx as nx
from matplotlib import pyplot as plt
from networkx.classes.reportviews import NodeView


def make_assert_message(left: Any, right: Any):
    """Creates an assert message. E.g.:
    LEFT:  [0, 1, 2]
    RIGHT: [0, 1, 4]"""
    return f"\n[LEFT]  {left} \n[RIGHT] {right}"


def assert_graphs_equal(actual_graphs: List[nx.Graph], expected_graphs: List[nx.Graph], node_data=True, edge_data=True):
    """Asserts 2 lists of NetworkX graphs are equal."""
    assert len(actual_graphs) == len(expected_graphs)
    for actual_graph, expected_graph in zip(actual_graphs, expected_graphs):
        assert_graph_equal(actual_graph, expected_graph, node_data=node_data, edge_data=edge_data)


def assert_graph_equal(
    graph1: nx.Graph,
    graph2: nx.Graph,
    node_data=True,
    edge_data=True,
):
    """Asserts 2 NetworkX graphs are equal."""
    assert_nodes_equal(list(graph1.nodes(data=node_data)), list(graph2.nodes(data=node_data)))
    assert_edges_equal(list(graph1.edges(data=edge_data)), list(graph2.edges(data=edge_data)))
    assert graph1.graph == graph2.graph, make_assert_message(graph1.graph, graph2.graph)


def assert_nodes_equal(nodes1: NodeView, nodes2: NodeView):
    """Asserts 2 nodes are equal."""
    assert sorted(nodes1) == sorted(nodes2), make_assert_message(nodes1, nodes2)


def assert_edges_equal(edges1: List, edges2: List):
    """Asserts 2 edges are equal."""
    assert sorted(edges1) == sorted(edges2), make_assert_message(edges1, edges2)


def draw_graph(graph: nx.Graph):
    """Draws a graph of NetworkX graph. Shows node id."""
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap("jet"), node_size=50)
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color="r", arrows=True)
    plt.show()
