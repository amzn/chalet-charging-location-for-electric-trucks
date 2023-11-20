# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import DEFAULT, Mock, patch

import pandas as pd

import chalet.algo.mip.helper as helper
import chalet.algo.mip.min_cost_pairs as min_cost
from chalet.algo.csp import time_feasible_path
from chalet.algo.util import remove_redundancy, remove_redundant_stations
from tests.algo.mip.helper import MipData
from tests.utility import get_path_module

STATION_SOL = MipData.station_sol
STATION_VARS = MipData.station_vars
CANDIDATES = MipData.candidates
NODES = MipData.nodes
OD_PAIRS = MipData.od_pairs
SUB_GRAPHS = MipData.sub_graphs


class TestMipMinCostPairs(unittest.TestCase):
    """Test mip min_cost_pairs."""

    @patch(
        get_path_module(helper.get_subgraph_indices_and_candidates),
        return_value=(pd.DataFrame(), [0], 0.0),
    )
    def test_min_cost_pairs_with_no_candidate_nodes(self, mock_indices_and_candidates):
        demand, cost = min_cost.min_cost_pairs(pd.DataFrame(), [], pd.DataFrame(), 0.0, 0.0, "")
        self.assertEqual(demand, 0.0)
        self.assertEqual(cost, 0)
        mock_indices_and_candidates.assert_called()

    @patch(
        get_path_module(helper.get_subgraph_indices_and_candidates),
        return_value=(CANDIDATES, [0], 10.0),
    )
    @patch(get_path_module(remove_redundant_stations), return_value=5.0)
    def test_min_cost_pairs_with_covered_demand(self, mock_remove_stations, mock_indices_and_candidates):
        with patch.multiple(
            min_cost,
            _construct_initial_solution=DEFAULT,
            _set_model_attributes_and_solve=DEFAULT,
            _build_model=DEFAULT,
        ) as mocks:
            mocks["_set_model_attributes_and_solve"].return_value = STATION_SOL
            demand, cost = min_cost.min_cost_pairs(NODES, SUB_GRAPHS, OD_PAIRS, 0.0, 1, "")
            self.assertEqual(demand, 11.0)
            self.assertEqual(cost, 5.0)
            for mock in mocks:
                mocks[mock].assert_called()

    @patch(get_path_module(helper.initialize_separator_constraints))
    @patch.object(min_cost.xp, "problem")
    def test_build_model(self, mock_xp, mock_constraints):
        min_cost._build_model(CANDIDATES, NODES, SUB_GRAPHS, OD_PAIRS, [0], STATION_VARS, "")
        mock_xp.assert_called_once()
        mock_constraints.assert_called_once()

    @patch(get_path_module(helper.get_cheapest_path), return_value=([0, 1], 5))
    @patch(get_path_module(helper.is_candidate), return_value=True)
    @patch(get_path_module(remove_redundancy), return_value=[0, 1])
    def test_construct_initial_solution(self, mock_redundancy, mock_is_candidate, mock_path_attributes):
        model = Mock()
        model.getIndex.return_value = 0
        min_cost._construct_initial_solution(model, CANDIDATES, NODES, OD_PAIRS, [0], SUB_GRAPHS, STATION_VARS)
        model.addmipsol.assert_called_once()

    @patch(get_path_module(helper.set_model_controls))
    def test_set_model_attributes_and_solve(self, mock_set_controls):
        model = Mock()
        min_cost._set_model_attributes_and_solve(
            model,
            STATION_VARS,
            [0],
            OD_PAIRS,
            NODES,
            SUB_GRAPHS,
            CANDIDATES,
            5.0,
            0.0,
        )
        model.getSolution.assert_called_with(STATION_VARS)
        model.solve.assert_called_once()
        mock_set_controls.assert_called_once()

    @patch(get_path_module(time_feasible_path), return_value=[0, 1])
    def test_pre_check_int_sol(self, mock_time_feasible_path):
        model = Mock()
        problem = Mock()
        check, cutoff = min_cost._pre_check_int_sol(
            problem, model, STATION_VARS, [0], OD_PAIRS, NODES, SUB_GRAPHS, 10.0
        )
        self.assertFalse(check)
        self.assertEqual(cutoff, 10.0)
        mock_time_feasible_path.assert_called_once()

    @patch(get_path_module(time_feasible_path), return_value=None)
    def test_pre_check_int_sol_without_feasible_path(self, mock_time_feasible_path):
        model = Mock()
        problem = Mock()
        check, cutoff = min_cost._pre_check_int_sol(
            problem, model, STATION_VARS, [0], OD_PAIRS, NODES, SUB_GRAPHS, 10.0
        )
        self.assertTrue(check)
        self.assertIsNone(cutoff)
        mock_time_feasible_path.assert_called_once()
