# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from chalet.preprocess.od_pairs_helpers import update_missing_od_demand


def test_data_without_demand():
    """Test for update_missing_od_demand without demand values"""
    actual = pd.DataFrame({"ORIGIN_ID": [1, 2, 3], "DESTINATION_ID": [2, 3, 4]})
    expected = actual.copy()
    expected["DEMAND"] = 1.0

    update_missing_od_demand(actual)

    assert_frame_equal(actual, expected)


def test_data_with_nan_demand():
    """Test for update_missing_od_demand with nan demand values"""
    actual = pd.DataFrame({"ORIGIN_ID": [1, 2, 3], "DESTINATION_ID": [2, 3, 4], "DEMAND": 3 * [np.nan]})
    expected = actual.copy()
    expected["DEMAND"] = 1.0

    update_missing_od_demand(actual)

    assert_frame_equal(actual, expected)
