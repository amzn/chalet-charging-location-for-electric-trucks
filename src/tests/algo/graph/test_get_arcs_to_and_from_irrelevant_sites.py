# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pandas.testing import assert_frame_equal

from chalet.algo.graph import _get_arcs_to_and_from_irrelevant_sites
from tests.algo.graph.graph_data import get_stub_arcs, get_stub_nodes


def test_get_arcs_to_and_from_irrelevant_sites():
    """Test for get_arcs_to_and_from_irrelevant_sites."""
    actual = get_stub_arcs()

    expected = _get_arcs_to_and_from_irrelevant_sites(get_stub_nodes(), get_stub_arcs(), 1, 4)

    assert_frame_equal(actual, expected)
