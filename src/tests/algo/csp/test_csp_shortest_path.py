# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Tuple

from chalet.algo import csp
from chalet.algo.csp import arc_road_time, arc_time
from tests.algo.csp.helper.invalid_way import InvalidWay
from tests.algo.csp.helper.two_way_diff_solution import TwoWayDiffSolution

INF_VALUE = float("inf")
EMPTY_GRAPH_SOLUTION: Tuple = ([], INF_VALUE)
ORIG = 1
DEST = 3


class TestShortestPath:
    """Tests for shortest_path."""

    def test_valid_graph_with_arc_road_time(self):
        """Test for a graph with two different solutions. The csp algorithm uses road time as weight."""
        result = csp.shortest_path(TwoWayDiffSolution.input_graph, ORIG, DEST, length=arc_road_time)

        assert result == TwoWayDiffSolution.sol.arc_road_time

    def test_invalid_graph_with_arc_road_time(self):
        """Test for a graph with no solution. The csp algorithm uses road time as weight."""
        result = csp.shortest_path(InvalidWay.input_graph, ORIG, DEST, length=arc_road_time)

        assert result == EMPTY_GRAPH_SOLUTION

    def test_valid_graph_with_road_time(self):
        """Test for a graph with two different solutions. The csp algorithm uses time as weight."""
        result = csp.shortest_path(TwoWayDiffSolution.input_graph, ORIG, DEST, length=arc_time)

        assert result == TwoWayDiffSolution.sol.arc_time_total

    def test_invalid_graph_with_road_time(self):
        """Test for a graph with no solution. The csp algorithm uses time as weight."""
        result = csp.shortest_path(InvalidWay.input_graph, ORIG, DEST, length=arc_time)

        assert result == EMPTY_GRAPH_SOLUTION
