# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pandas.testing import assert_frame_equal

from chalet.model.processed_od_pairs import OdPairs
from chalet.preprocess.od_pairs_helpers import add_direct_distances
from tests.preprocess.stub_data import get_stub_od_pairs, get_stub_time_dist_map


def test_add_direct_distances():
    """Test for add_direct_distances"""
    time_dist_map = get_stub_time_dist_map()
    actual = get_stub_od_pairs()
    expected = actual.copy()
    expected[OdPairs.distance] = 10

    add_direct_distances(time_dist_map, actual)

    assert_frame_equal(actual, expected)
