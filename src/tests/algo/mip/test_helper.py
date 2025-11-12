# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import Mock, patch

import networkx
import numpy as np

import chalet.algo.csp as csp
import chalet.algo.mip.helper as helper
import chalet.algo.util as util
from tests.algo.mip.helper import MipData
from tests.utility import get_path_module

NODES = MipData.nodes
SUB_GRAPHS = MipData.sub_graphs
OD_PAIRS = MipData.od_pairs
STATION_VARS = MipData.station_vars
DEMAND_VARS = MipData.demand_vars


class TestMipHelper(unittest.TestCase):
    """Test mip helper methods."""

    @patch(get_path_module(util.check_pair_coverage))
    def test_get_subgraph_indices_and_candidates(self, mock_pair_coverage):
        candidates, indices, demand = helper.get_subgraph_indices_and_candidates(
            MipData.od_pairs_feasible, NODES, SUB_GRAPHS
        )
        self.assertListEqual(indices, [0])
        np.all(candidates == [0, 1, 2])
        self.assertEqual(demand, 0)
        mock_pair_coverage.assert_called_once()

    @patch(get_path_module(helper._add_separator))
    def test_initialize_separator_constraints(self, mock_separator):
        model = Mock()
        helper.initialize_separator_constraints(model, NODES, SUB_GRAPHS, OD_PAIRS, [0], STATION_VARS)
        mock_separator.assert_called()

    @patch("networkx.set_node_attributes")
    @patch(get_path_module(csp.time_feasible_cheapest_path), return_value=([0, 1], 5.0))
    def test_get_path_attributes(self, mock_csp_cheapest_path, mock_nx_set_node_attributes):
        path, cost = helper.get_cheapest_path(OD_PAIRS, 0, SUB_GRAPHS, NODES, [0])
        mock_csp_cheapest_path.assert_called_with(SUB_GRAPHS[0], 0, 1, 3.0, 5.0)
        self.assertListEqual(path, [0, 1])
        self.assertEqual(cost, 5.0)

    @patch("networkx.dfs_preorder_nodes", return_value=[0, 1])
    def test_add_separator_invalid_out_component(self, mock_preorder_nodes):
        sub_graph = SUB_GRAPHS[0]
        reverse_graph = networkx.reverse_view(sub_graph)
        model = Mock()
        helper._add_separator(sub_graph, reverse_graph, 0, 1, NODES, DEMAND_VARS, STATION_VARS, model, 0)
        model.addConstraint.assert_not_called()

    @patch("networkx.dfs_preorder_nodes", return_value=[0, 1])
    @patch("networkx.node_boundary", return_value=[-1])
    def test_add_separator_throws_runtime_error(self, mock_node_boundary, mock_preorder_nodes):
        with self.assertRaises(RuntimeError):
            sub_graph = SUB_GRAPHS[0]
            reverse_graph = networkx.reverse_view(sub_graph)
            model = Mock()
            helper._add_separator(sub_graph, reverse_graph, 0, 2, NODES, DEMAND_VARS, STATION_VARS, model, 0)

    def test_is_candidate_true(self):
        is_candidate = helper.is_candidate(0, NODES)
        self.assertTrue(is_candidate)

    def test_is_candidate_false(self):
        is_candidate = helper.is_candidate(-1, NODES)
        self.assertFalse(is_candidate)

    def test_set_model_controls_max_demand(self):
        model = Mock()
        helper.set_model_controls(model, 10.0, 0.0)
        self.assertEqual(model.setControl.call_count, 9)

    def test_set_model_controls_min_cost(self):
        model = Mock()
        helper.set_model_controls(model, 10.0, 0.0)
        self.assertEqual(model.setControl.call_count, 9)

    @patch(get_path_module(util.check_solution), return_value=(5.0, 10.0))
    def test_verify_model_output(self, mock_check_sol):
        helper.verify_model_output(NODES, SUB_GRAPHS, MipData.od_pairs_feasible, 10.0, 20.0)
        mock_check_sol.assert_called_once()
