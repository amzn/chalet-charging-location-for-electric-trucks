# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Tuple

import pytest

from chalet.algo.csp import _road_time_bounded_fastest_path
from tests.algo.csp.helper.circle_way import CircleWay
from tests.algo.csp.helper.complex_way import ComplexWay
from tests.algo.csp.helper.five_way import FiveWay
from tests.algo.csp.helper.invalid_way import InvalidWay
from tests.algo.csp.helper.multiple_way_with_multiple_lagrange import MultipleWayWithMultipleLagrange
from tests.algo.csp.helper.one_way import OneWay
from tests.algo.csp.helper.two_way_diff_solution import TwoWayDiffSolution
from tests.algo.csp.helper.two_way_diff_solution_equal_road_time import TwoWayDiffSolutionEqualRoadTime
from tests.algo.csp.helper.two_way_diff_solution_equal_total_road_time import TwoWayDiffSolutionEqualTotalRoadTime
from tests.algo.csp.helper.two_way_equal_solution import TwoWayEqualSolution
from tests.algo.csp.helper.ways import Ways
from tests.algo.csp.helper.zero_road_time_way import ZeroRoadTimeWay

INF_VALUE = float("inf")
EMPTY_GRAPH_SOLUTION: Tuple = ([], INF_VALUE)
ORIG = 1
DEST = 3


@pytest.mark.parametrize(
    "graph",
    [
        OneWay,
        MultipleWayWithMultipleLagrange,
        TwoWayEqualSolution,
        TwoWayDiffSolution,
        TwoWayDiffSolutionEqualRoadTime,
        TwoWayDiffSolutionEqualTotalRoadTime,
        FiveWay,
        CircleWay,
        ComplexWay,
        ZeroRoadTimeWay,
        InvalidWay,
    ],
)
class TestRoadTimeBoundedFastestPath:
    """Tests for road_time_bounded_fastest_path."""

    def test_arc_road_time_total_bound(self, graph: Ways):
        """Test for a graph with arc road time total bound"""
        result = _road_time_bounded_fastest_path(graph.input_graph, ORIG, DEST, graph.time.arc_road_time_total)

        assert result == graph.sol.arc_time_total

    def test_arc_time_total_bound(self, graph: Ways):
        """Test for a graph with arc time total bound"""
        result = _road_time_bounded_fastest_path(graph.input_graph, ORIG, DEST, graph.time.arc_time_total)

        assert result == graph.sol.arc_time_total

    def test_arc_time_bound(self, graph: Ways):
        """Test for a graph with arc time bound"""
        result = _road_time_bounded_fastest_path(graph.input_graph, ORIG, DEST, graph.time.arc_time)

        assert result == graph.sol.arc_time_total

    def test_arc_road_time_bound(self, graph: Ways):
        """Test for a graph with road time bound"""
        result = _road_time_bounded_fastest_path(graph.input_graph, ORIG, DEST, graph.time.arc_road_time)

        assert result == graph.sol.arc_road_time_total

    def test_valid_graph_with_negative_bound(self, graph: Ways):
        """Test for a graph with a negative bound"""
        result = _road_time_bounded_fastest_path(graph.input_graph, ORIG, DEST, -1)

        assert result == EMPTY_GRAPH_SOLUTION
