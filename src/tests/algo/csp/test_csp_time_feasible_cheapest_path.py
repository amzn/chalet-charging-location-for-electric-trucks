# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from chalet.algo.csp import time_feasible_cheapest_path
from tests.algo.csp.helper.complex_way import ComplexWay
from tests.algo.csp.helper.invalid_way import InvalidWay
from tests.algo.csp.helper.multiple_way_with_multiple_lagrange import MultipleWayWithMultipleLagrange
from tests.algo.csp.helper.one_way import OneWay
from tests.algo.csp.helper.two_way_diff_solution import TwoWayDiffSolution
from tests.algo.csp.helper.ways import EMPTY_GRAPH_SOLUTION, Ways

ORIG = 1
DEST = 3


@pytest.mark.parametrize(
    "graph",
    [
        OneWay,
        TwoWayDiffSolution,
        ComplexWay,
        MultipleWayWithMultipleLagrange,
        InvalidWay,
    ],
)
class TestTimeFeasibleCheapestPath:
    """Tests for time_feasible_cheapest_path."""

    def test_road_time_and_road_time_total(self, graph: Ways):
        """Test for a graph with road time and road time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_road_time,
            graph.time.arc_road_time_total,
        )

        assert result == graph.sol_cost.road_time_and_road_time_total

    def test_time_and_road_time_total(self, graph: Ways):
        """Test for a graph with time and road time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_time,
            graph.time.arc_road_time_total,
        )

        assert result == graph.sol_cost.time_and_road_time_total

    def test_road_time_and_time_total(self, graph: Ways):
        """Test for a graph with road time and time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_road_time,
            graph.time.arc_time_total,
        )

        assert result == graph.sol_cost.road_time_and_time_total

    def test_time_and_time_total(self, graph: Ways):
        """Test for a graph with time and time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_time,
            graph.time.arc_time_total,
        )

        assert result == graph.sol_cost.time_and_time_total

    def test_road_time_and_zero(self, graph: Ways):
        """Test for a graph with road time and zero bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_road_time,
            0,
        )

        assert result == EMPTY_GRAPH_SOLUTION

    def test_time_and_zero(self, graph: Ways):
        """Test for a graph with time and zero bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            graph.time.arc_time,
            0,
        )

        assert result == EMPTY_GRAPH_SOLUTION

    def test_zero_and_road_time_total(self, graph: Ways):
        """Test for a graph with zero and road time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            0,
            graph.time.arc_time_total,
        )

        assert result == EMPTY_GRAPH_SOLUTION

    def test_zero_and_time_total(self, graph: Ways):
        """Test for a graph with zero and time total bounds"""
        result = time_feasible_cheapest_path(
            graph.input_graph,
            ORIG,
            DEST,
            0,
            graph.time.arc_time_total,
        )

        assert result == EMPTY_GRAPH_SOLUTION
