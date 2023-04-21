# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from unittest.mock import patch

import pandas as pd

from chalet.algo import util
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


def mock_check_pair_coverage(nodes, subgraphs, od_pairs):
    pass


@patch.object(util, "check_pair_coverage")
def test_check_solution(patch_object):
    nodes = pd.DataFrame({Nodes.real: [False, True, True, True], Nodes.cost: [1.0, 2.0, 3.0, 4.0]})
    od_pairs = pd.DataFrame({OdPairs.covered: [False, True, True, True], OdPairs.demand: 4 * [2.0]})

    actual_sol_demand, actual_sol_cost = util.check_solution(nodes, Any, od_pairs, 0, 0)

    assert actual_sol_demand == 6.0
    assert actual_sol_cost == 9.0
    patch_object.assert_called_with(nodes, Any, od_pairs)
