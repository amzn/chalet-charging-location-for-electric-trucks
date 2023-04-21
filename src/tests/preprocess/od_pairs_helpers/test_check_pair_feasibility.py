# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import networkx as nx
import pandas as pd
from pandas.testing import assert_frame_equal

from chalet.model.processed_arcs import Arcs
from chalet.model.processed_od_pairs import OdPairs
from chalet.preprocess.od_pairs_helpers import check_pair_feasibility
from tests.preprocess.stub_data import get_stub_processed_od_pairs


def test_check_pair_feasibility():
    """Test for check_pair_feasibility"""
    actual = get_stub_processed_od_pairs()
    actual[OdPairs.max_road_time] = pd.Series([1, 0, 1])
    actual[OdPairs.max_time] = pd.Series([3, 3, 2])
    graph1 = nx.DiGraph()
    graph2 = nx.DiGraph()
    graph3 = nx.DiGraph()
    attr = {Arcs.time: 1, Arcs.fuel_time: 1, Arcs.break_time: 1}
    graph1.add_edges_from([(1, 2)], **attr)
    graph2.add_edges_from([(2, 3)], **attr)
    graph3.add_edges_from([(3, 4)], **attr)
    subgraphs = [graph1, graph2, graph3]
    expected = actual.copy()
    expected[OdPairs.feasible] = pd.Series([True, False, False])

    check_pair_feasibility(subgraphs, actual)

    assert_frame_equal(actual, expected)
