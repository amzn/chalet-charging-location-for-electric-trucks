# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

import chalet.algo.util as ut
from chalet.model.processed_nodes import Nodes


def mock_redundancy(solution, nodes, subgraphs, od_pairs):
    nodes[Nodes.real] = False
    return [0, 1]


@patch.object(ut, "remove_redundancy", side_effect=mock_redundancy)
def test_remove_redundant_stations(patch_object):
    actual_nodes = pd.DataFrame(
        {
            Nodes.cost: [0.0, 1.0, 1.0, 0.0],
            Nodes.real: [False, False, True, True],
        }
    )
    expected_nodes = actual_nodes.copy()
    expected_nodes[Nodes.real] = [True, True, False, False]
    expected = 1.0

    actual = ut.remove_redundant_stations(actual_nodes, Any, Any)

    assert_frame_equal(actual_nodes, expected_nodes)
    assert actual == expected
