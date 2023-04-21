# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from unittest.mock import patch

from chalet.algo import csp
from tests.utility import get_path_module

PATH = [1, 2, 3]
INF_VALUE = float("inf")
UNUSED = Any
ORIG = 1
DEST = 3


class TestTimeFeasiblePath:
    """Tests for time_feasible_path."""

    @patch(get_path_module(csp._road_time_bounded_fastest_path), return_value=(PATH, INF_VALUE))
    @patch(get_path_module(csp._time_bounded_fastest_road_path), return_value=(PATH, 1))
    def test_inf_path_time_and_valid_path_road_time(self, patch1, patch2):
        """Test a graph with an infinite path time and a valid road time"""
        result = csp.time_feasible_path(UNUSED, UNUSED, UNUSED, INF_VALUE, INF_VALUE)

        assert result == []

    @patch(get_path_module(csp._road_time_bounded_fastest_path), return_value=(PATH, INF_VALUE))
    @patch(get_path_module(csp._time_bounded_fastest_road_path), return_value=(PATH, INF_VALUE))
    def test_inf_path_time_and_inf_path_road_time(self, patch1, patch2):
        """Test a graph with an infinite path time and an infinite path road time"""
        result = csp.time_feasible_path(UNUSED, UNUSED, UNUSED, INF_VALUE, INF_VALUE)

        assert result == []

    @patch(get_path_module(csp._road_time_bounded_fastest_path), return_value=(PATH, 1))
    @patch(get_path_module(csp._time_bounded_fastest_road_path), return_value=([], 3))
    def test_valid_path_time_and_invalid_path_road_time(self, patch1, patch2):
        """Test a graph with a valid path time and an infinite path road time"""
        result = csp.time_feasible_path(UNUSED, UNUSED, UNUSED, 2, 1)

        assert result == PATH

    @patch(get_path_module(csp._road_time_bounded_fastest_path), return_value=([], 3))
    @patch(get_path_module(csp._time_bounded_fastest_road_path), return_value=(PATH, 1))
    def test_invalid_path_time_and_valid_path_road_time(self, patch1, patch2):
        """Test a graph with an invalid path time and a valid path road time"""
        result = csp.time_feasible_path(UNUSED, UNUSED, UNUSED, 1, 2)

        assert result == PATH

    @patch(get_path_module(csp._road_time_bounded_fastest_path), return_value=(PATH, 2))
    @patch(get_path_module(csp._time_bounded_fastest_road_path), return_value=(PATH, 2))
    def test_invalid_path_time_and_invalid_path_road_time(self, patch1, patch2):
        """Test a graph with an invalid path time and an invalid path road time"""
        result = csp.time_feasible_path(UNUSED, UNUSED, UNUSED, 1, 1)

        assert result == []
