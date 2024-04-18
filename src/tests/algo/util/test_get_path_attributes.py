# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from unittest.mock import ANY, patch

import networkx as nx
import pandas as pd

from chalet.algo import csp
from chalet.algo.util import get_feasible_path
from chalet.model.processed_od_pairs import OdPairs


def time_feasible_path_mock(subgraph, orig, dest, max_road_time, max_time):
    return 10


@patch.object(csp, "time_feasible_path", side_effect=time_feasible_path_mock)
def test_get_path_attributes(patch_object):
    od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [2],
            OdPairs.destination_id: [69],
            OdPairs.max_time: [100.0],
            OdPairs.max_road_time: [200.0],
        }
    )

    empty_graph = nx.DiGraph()
    actual = get_feasible_path(empty_graph, 0, od_pairs, Any)

    assert actual == 10
    patch_object.assert_called_with(ANY, 2, 69, 200.0, 100.0)
