# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pandas.testing import assert_frame_equal

from chalet.algo.graph import _filter_arcs_based_on_transit_time_lower_bounds
from tests.algo.graph.graph_data import get_stub_arcs, get_stub_time_dist_map

INF_VALUE = float("inf")


def test_no_bound():
    """Test for filter_arcs_based_on_transit_time_lower_bound. Uses infinite values as bounds."""
    expected = get_stub_arcs()

    actual = _filter_arcs_based_on_transit_time_lower_bounds(
        get_stub_time_dist_map(),
        get_stub_arcs(),
        orig=1,
        dest=4,
        truck_range=300,
        fuel_time_bound=75,
        max_time=INF_VALUE,
        max_road_time=INF_VALUE,
    )

    assert_frame_equal(actual, expected)


def test_road_time_bound():
    """Test for filter_arcs_based_on_transit_time_lower_bound.
    Uses a max_time bound and an infinite time max_road_time bound."""
    expected = get_stub_arcs()
    expected.drop(list(range(12)), inplace=True)

    actual = _filter_arcs_based_on_transit_time_lower_bounds(
        get_stub_time_dist_map(),
        get_stub_arcs(),
        orig=1,
        dest=4,
        truck_range=300,
        fuel_time_bound=75,
        max_time=25,
        max_road_time=INF_VALUE,
    )

    assert_frame_equal(actual, expected)


def test_time_bound():
    """Test for filter_arcs_based_on_transit_time_lower_bound.
    Uses a max_road_time bound and an infinite time max_time bound."""
    expected = get_stub_arcs()
    expected.drop(list(range(12)), inplace=True)

    actual = _filter_arcs_based_on_transit_time_lower_bounds(
        get_stub_time_dist_map(),
        get_stub_arcs(),
        orig=1,
        dest=4,
        truck_range=300,
        fuel_time_bound=75,
        max_time=INF_VALUE,
        max_road_time=20,
    )

    assert_frame_equal(actual, expected)
