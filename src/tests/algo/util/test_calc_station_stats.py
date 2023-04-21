# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import ANY, call, patch

import networkx as nx
import pandas as pd
from pandas.testing import assert_frame_equal

from chalet.algo import util
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


def mock_get_path_attributes():
    return


@patch.object(util, "get_path_attributes", side_effect=[[1, 5, 6, 2], [2, 7, 8, 3], [3, 4]])
def test_calc_station_stats(patch_object):
    battery_capacity = 540
    terminal_range = 125.0
    truck_range = 300
    actual_nodes = pd.DataFrame(
        {Nodes.type: ["SITE", "SITE", None, None, "SITE", "SITE", "SITE", None]}, index=[1, 2, 3, 4, 5, 6, 7, 8]
    )
    # calc_station_stats requires access to the following fields
    actual_nodes[Nodes.real] = [True, True, False, False, True, True, True, False]
    actual_nodes[Nodes.cost] = [0] * len(actual_nodes)

    expected_nodes = actual_nodes.copy()
    expected_nodes[Nodes.energy] = [0, 0, 0, 0, 243, 243, 18, 18]
    expected_nodes[Nodes.demand] = [0.0, 0.0, 0.0, 0.0, 10.0, 10.0, 20.0, 20.0]
    graph1 = nx.DiGraph()
    graph1.add_edges_from([(1, 5), (5, 6), (6, 2)], **{Nodes.distance: 10.0})
    graph2 = nx.DiGraph()
    graph2.add_edges_from([(2, 7), (7, 8), (8, 3)], **{Nodes.distance: 10.0})
    graph3 = nx.DiGraph()
    graph3.add_edge(3, 4, **{Nodes.distance: 10.0})
    subgraphs = [graph1, graph2, graph3]
    actual_od_pairs = pd.DataFrame(
        {OdPairs.origin_id: [1, 2, 3], OdPairs.destination_id: [2, 3, 4], OdPairs.demand: [10.0, 20.0, 30.0]}
    )
    expected_od_pairs = actual_od_pairs.copy()

    actual = util.calc_station_stats(
        actual_nodes, subgraphs, actual_od_pairs, battery_capacity, terminal_range, truck_range
    )

    assert actual == {(1, 2): [5, 6], (2, 3): [7, 8], (3, 4): []}
    assert_frame_equal(actual_nodes, expected_nodes)
    assert_frame_equal(actual_od_pairs, expected_od_pairs)
    patch_object.assert_has_calls([call(subgraphs[i], i, actual_od_pairs, ANY) for i in range(3)])
