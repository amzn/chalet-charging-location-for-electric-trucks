# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx
import pandas as pd
import pytest

from chalet.algo.util import remove_redundancy
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


@pytest.mark.parametrize("value, expected", [(0.0, [1, 2, 3, 4]), (100.0, [])])
def test_remove_redundancy(value, expected):
    nodes = pd.DataFrame(
        {
            Nodes.id: [1, 2, 3, 4],
            Nodes.type: 4 * [0.0],
            Nodes.latitude: [0.0, 10.0, 0.0, 10.0],
            Nodes.longitude: [0.0, 0.0, 10.0, 10.0],
            Nodes.name: ["node1", "node2", "node3", "node4"],
            Nodes.cost: 4 * [1.0],
            Nodes.real: 4 * [False],
        },
        index=[1, 2, 3, 4],
    )
    od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3],
            OdPairs.destination_id: [2, 3, 4],
            OdPairs.demand: [10.0, 20.0, 30.0],
            OdPairs.distance: [10.0, 40.0, 60.0],
            OdPairs.distance: [10.0, 40.0, 60.0],
            OdPairs.legs: 3 * [1],
            OdPairs.max_time: [40.0, 80.0, 120.0],
            OdPairs.max_road_time: [40.0, 80.0, 120.0],
            OdPairs.feasible: 3 * [True],
            OdPairs.covered: 3 * [False],
        }
    )
    solution = [1, 2, 3, 4]
    graph = nx.DiGraph()
    graph.add_edges_from([(1, 2), (2, 3), (3, 4)], **{Arcs.time: value, Arcs.break_time: value, Arcs.fuel_time: value})
    subgraphs = [graph.copy(), graph.copy(), graph.copy()]

    actual = remove_redundancy(solution, nodes, subgraphs, od_pairs)

    assert actual == expected
