# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from pandas.testing import assert_frame_equal

from chalet.preprocess.od_pairs_helpers import remove_od_with_same_orig_dest
from tests.preprocess.stub_data import get_stub_od_coverage


def test_make_od_pairs():
    """Test for remove_od_with_same_orig_dest"""
    expected = get_stub_od_coverage()
    invalid_row = pd.DataFrame(
        {"ORIGIN_ID": [5], "DESTINATION_ID": [5], "DEMAND": [40.0], "DISTANCE": [20]},
        index=[13],
    )
    actual = pd.concat([expected, invalid_row])

    actual = remove_od_with_same_orig_dest(actual)

    assert_frame_equal(actual, expected)
