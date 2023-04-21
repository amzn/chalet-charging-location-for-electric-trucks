# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pandas as pd
from pandas.testing import assert_frame_equal

from chalet.model.processed_od_pairs import OdPairs
from chalet.preprocess.od_pairs_helpers import aggregate_identical_od_pairs
from tests.preprocess.stub_data import get_stub_od_coverage


def test_aggregate_identical_od_pairs():
    """Test for aggregate_identical_od_pairs"""
    od_pairs = get_stub_od_coverage()
    identical_od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [5, 5, 6, 6, 6],
            OdPairs.destination_id: [6, 6, 7, 7, 7],
            OdPairs.demand: 5 * [10.0],
            OdPairs.distance: 5 * [10],
        }
    )
    aggregated_identical_od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [5, 6],
            OdPairs.destination_id: [6, 7],
            OdPairs.demand: [20.0, 30.0],
            OdPairs.distance: 2 * [10],
        },
        index=[3, 4],
    )
    actual = pd.concat([od_pairs, identical_od_pairs])
    expected = pd.concat([od_pairs, aggregated_identical_od_pairs])
    expected[OdPairs.legs] = 1

    aggregate_identical_od_pairs(actual)

    assert_frame_equal(actual, expected)
