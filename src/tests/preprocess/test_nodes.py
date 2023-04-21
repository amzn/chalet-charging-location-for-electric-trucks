# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from pandas.testing import assert_series_equal

from chalet.model.input.node import Node
from chalet.model.processed_nodes import Nodes
from chalet.preprocess.nodes import PreprocessNodes


class TestPreprocessNodes:
    def test_preprocess(self):
        test_nodes = pd.DataFrame(
            {
                "ID": [0, 1, 2, 3],
                "TYPE": ["SITE", "SITE", "STATION", "STATION"],
                "COST": [0.0, 1.0, 1.0, 0.0],
            }
        )
        test_data = {Node.get_file_name(): test_nodes}
        expected = pd.Series([True, False, False, True], name=Nodes.real)
        pn = PreprocessNodes()

        pn.preprocess(test_data)
        actual = test_data[Node.get_file_name()][Nodes.real]

        assert_series_equal(expected, actual)
