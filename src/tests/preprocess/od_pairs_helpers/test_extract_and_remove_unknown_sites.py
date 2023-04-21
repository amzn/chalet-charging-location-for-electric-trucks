# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from chalet.common.constants import UNKNOWN_SITES
from chalet.model.input.node import Node
from chalet.preprocess.od_pairs_helpers import extract_and_remove_unknown_sites
from tests.preprocess.stub_data import get_stub_nodes, get_stub_od_pairs


def test_extract_and_remove_unknown_sites():
    """Test for extract_and_remove_unknown_sites"""
    actual_od_pairs = get_stub_od_pairs()
    expected_od_pairs = actual_od_pairs.copy()
    expected_od_pairs.drop([0, 1], inplace=True)
    expected_od_pairs.reset_index(drop=True, inplace=True)
    nodes = get_stub_nodes()
    nodes["ID"] = 2 * [np.nan] + [3, 4]
    actual_data = {Node.get_file_name(): nodes}
    expected_data = actual_data.copy()
    expected_data[UNKNOWN_SITES] = pd.Series([1, 2])

    extract_and_remove_unknown_sites(actual_od_pairs, actual_data)

    assert_frame_equal(actual_od_pairs, expected_od_pairs)
    assert_frame_equal(actual_data[Node.get_file_name()], expected_data[Node.get_file_name()])
    assert_series_equal(actual_data[UNKNOWN_SITES], expected_data[UNKNOWN_SITES])
