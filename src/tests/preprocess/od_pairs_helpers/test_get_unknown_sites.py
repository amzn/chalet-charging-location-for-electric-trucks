# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from chalet.preprocess.od_pairs_helpers import get_unknown_sites
from tests.preprocess.stub_data import get_stub_nodes, get_stub_od_pairs


def test_id_partially_equal_nan():
    """Test for get_unknown_sites with node id partially equal to nan"""
    nodes = get_stub_nodes()
    nodes["ID"] = 2 * [np.nan] + [3, 4]
    od_pairs = get_stub_od_pairs()
    expected = pd.Series([1, 2])

    actual = get_unknown_sites(od_pairs, nodes)

    assert_series_equal(actual, expected)


def test_id_equal_nan():
    """Test for get_unknown_sites with node id equal to nan"""
    nodes = get_stub_nodes()
    nodes["ID"] = np.nan
    od_pairs = get_stub_od_pairs()
    expected = pd.Series([1, 2, 3, 4], index=[0, 1, 2, 5])

    actual = get_unknown_sites(od_pairs, nodes)

    assert_series_equal(actual, expected)


def test_no_unknown_sites():
    """Test for get_unknown_sites with no unknown sites"""
    nodes = get_stub_nodes()
    od_pairs = get_stub_od_pairs()

    result = get_unknown_sites(od_pairs, nodes)

    assert len(result) == 0
