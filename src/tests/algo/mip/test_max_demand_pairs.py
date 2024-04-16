# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import DEFAULT, Mock, patch

import pandas as pd

import chalet.algo.mip.helper as helper
import chalet.algo.mip.max_demand_pairs as max_demand
import chalet.algo.util as util
from chalet.model.processed_nodes import Nodes
from tests.algo.mip.helper import MipData
from tests.utility import get_path_module

CANDIDATES = MipData.candidates
NODES = MipData.nodes
OD_PAIRS = MipData.od_pairs
SUB_GRAPHS = MipData.sub_graphs
DEMAND_SOL = MipData.demand_sol
STATION_SOL = MipData.station_sol
DEMAND_VARS = MipData.demand_vars
STATION_VARS = MipData.station_vars


class TestMipMaxDemandPairs(unittest.TestCase):
    """Test mip max_demand_pairs."""

    @patch(
        get_path_module(helper.get_subgraph_indices_and_candidates),
        return_value=(pd.DataFrame(), [0], 0.0),
    )
    def test_max_demand_pairs_with_no_candidate_nodes(self, mock_indices_and_candidates):
        demand, cost = max_demand.max_demand_pairs(pd.DataFrame(), [], pd.DataFrame(), 0.0, 0.0, 1, "")
        mock_indices_and_candidates.assert_called()
        self.assertEqual(demand, 0.0)
        self.assertEqual(cost, 0)

    @patch(
        get_path_module(helper.get_subgraph_indices_and_candidates),
        return_value=(CANDIDATES, [0], 10.0),
    )
    def test_max_demand_pairs_with_covered_demand(self, mock_indices_and_candidates):
        with patch.multiple(
            max_demand,
            _construct_initial_solution=DEFAULT,
            _set_model_attributes_and_solve=DEFAULT,
            _build_model=DEFAULT,
        ) as mocks:
            mocks["_set_model_attributes_and_solve"].return_value = (DEMAND_SOL, STATION_SOL)
            demand, cost = max_demand.max_demand_pairs(NODES, SUB_GRAPHS, OD_PAIRS, 10.0, 0.0, 1, "")
            self.assertEqual(demand, 11.0)
            for mock in mocks:
                mocks[mock].assert_called()

    @patch(get_path_module(helper.initialize_separator_constraints))
    @patch.object(max_demand.xp, "problem")
    def test_build_model(self, mock_xp, mock_constraints):
        max_demand._build_model(CANDIDATES, NODES, SUB_GRAPHS, OD_PAIRS, [0], 10.0, DEMAND_VARS, STATION_VARS, "")
        mock_xp.assert_called_once()
        mock_constraints.assert_called_once()

    @patch(get_path_module(helper.set_model_controls))
    def test_set_model_attributes_and_solve(self, mock_set_controls):
        model = Mock()
        max_demand._set_model_attributes_and_solve(
            model,
            DEMAND_VARS,
            OD_PAIRS,
            NODES,
            STATION_VARS,
            [0],
            SUB_GRAPHS,
            CANDIDATES,
            5.0,
            0.0,
            2.0,
        )
        model.getSolution.assert_called()
        model.solve.assert_called_once()

    @patch(get_path_module(helper.get_path_attributes), return_value=([0, 1], 5.0))
    @patch(get_path_module(helper.is_candidate), return_value=True)
    def test_construct_initial_solution_with_station_nodes(self, mock_is_candidate, mock_path_attributes):
        model = Mock()
        max_demand._construct_initial_solution(model, CANDIDATES, NODES, OD_PAIRS, [0], SUB_GRAPHS, 10.0)
        model.addmipsol.assert_called_with([1, 1, 1])

    @patch(get_path_module(helper.get_path_attributes), return_value=([0, 1], 11.0))
    @patch(get_path_module(helper.is_candidate), return_value=True)
    def test_construct_initial_solution_with_higher_min_cost(self, mock_is_candidate, mock_path_attributes):
        model = Mock()
        nodes = NODES.copy()
        nodes[Nodes.cost] = [11, 15, 20]
        max_demand._construct_initial_solution(model, CANDIDATES, nodes, OD_PAIRS, [0], SUB_GRAPHS, 10.0)
        model.addmipsol.assert_called_with([0, 0, 0])

    @patch(get_path_module(helper.get_path_attributes), return_value=([0, 1], 20.0))
    @patch(get_path_module(helper.is_candidate), return_value=True)
    def test_construct_initial_solution_with_higher_path_cost(self, mock_is_candidate, mock_path_attributes):
        model = Mock()
        max_demand._construct_initial_solution(model, CANDIDATES, NODES, OD_PAIRS, [0], SUB_GRAPHS, 10.0)
        model.addmipsol.assert_called_with([0, 0, 0])

    @patch(get_path_module(util.get_path_attributes), return_value=[0])
    def test_check_int_sol(self, mock_path_attributes):
        model = Mock()
        problem = Mock()

        def mock_lpsol(a, b, c, d):
            a.append(0)

        problem.getlpsol.side_effect = mock_lpsol
        model.getIndex.return_value = 0
        max_demand._check_int_sol(problem, model, DEMAND_VARS, OD_PAIRS, NODES, STATION_VARS, [0], SUB_GRAPHS)
        problem.loadmipsol.assert_called_once()

    @patch(get_path_module(util.get_path_attributes), return_value=None)
    def test_check_int_sol_without_path(self, mock_path_attributes):
        model = Mock()
        problem = Mock()

        def mock_lpsol(a, b, c, d):
            a.append(0)

        problem.getlpsol.side_effect = mock_lpsol
        model.getIndex.return_value = 0
        max_demand._check_int_sol(problem, model, DEMAND_VARS, OD_PAIRS, NODES, STATION_VARS, [0], SUB_GRAPHS)
        problem.loadmipsol.assert_not_called()

    def test_pre_check_int_sol_without_soltype(self):
        model = Mock()
        problem = Mock()
        check, cutoff = max_demand._pre_check_int_sol(
            problem, 0, 0, model, DEMAND_VARS, OD_PAIRS, NODES, STATION_VARS, [0], SUB_GRAPHS
        )
        self.assertFalse(check)
        self.assertEqual(cutoff, 0)
