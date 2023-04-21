# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from chalet.algo.util import check_pair_coverage
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


@pytest.mark.parametrize(
    "cost, time, feasible, nodes_real, expected_covered",
    [
        (1.0, 0.0, True, True, True),
        (0.0, 0.0, True, True, True),
        (1.0, 1000.0, True, True, False),
        (1.0, 0.0, False, True, True),
        (1.0, 0.0, True, False, False),
    ],
)
def test_check_pair_coverage(cost, time, feasible, nodes_real, expected_covered):
    nodes = pd.DataFrame(
        {
            Nodes.id: [1, 2, 3, 4],
            Nodes.type: 4 * [0.0],
            Nodes.latitude: [0.0, 10.0, 0.0, 10.0],
            Nodes.longitude: [0.0, 0.0, 10.0, 10.0],
            Nodes.name: ["node1", "node2", "node3", "node4"],
            Nodes.cost: 4 * [cost],
            Nodes.real: 4 * [nodes_real],
        },
        index=[1, 2, 3, 4],
    )
    actual_od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3],
            OdPairs.destination_id: [2, 3, 4],
            OdPairs.demand: [10.0, 20.0, 30.0],
            OdPairs.distance: [10.0, 40.0, 60.0],
            OdPairs.legs: 3 * [1],
            OdPairs.max_time: [40.0, 80.0, 120.0],
            OdPairs.max_road_time: [40.0, 80.0, 120.0],
            OdPairs.feasible: 3 * [feasible],
        }
    )
    expected_od_pairs = actual_od_pairs.copy()
    expected_od_pairs[OdPairs.covered] = expected_covered
    graph = nx.DiGraph()
    graph.add_edges_from([(1, 2), (2, 3), (3, 4)], **{Arcs.time: time, Arcs.break_time: time, Arcs.fuel_time: time})
    subgraphs = [graph.copy(), graph.copy(), graph.copy()]

    check_pair_coverage(nodes, subgraphs, actual_od_pairs)

    assert_frame_equal(actual_od_pairs, expected_od_pairs)
