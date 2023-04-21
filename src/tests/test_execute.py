# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import pandas as pd

import chalet.execute as execute
from chalet.common.constants import OD_COVERAGE, SUB_GRAPHS, UNKNOWN_SITES
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters

context = {
    Node.get_file_name(): pd.DataFrame(),
    Parameters.get_file_name(): Parameters({}),
    OdPair.get_file_name(): pd.DataFrame(),
    SUB_GRAPHS: [],
    OD_COVERAGE: pd.DataFrame(),
    UNKNOWN_SITES: pd.DataFrame(),
}


class TestExecute:
    @patch.object(execute, "get_all_inputs")
    @patch.object(execute, "export_data")
    @patch.object(execute.PostProcess, "postprocess")
    @patch.object(execute.Executor, "_preprocess")
    @patch.object(execute.Executor, "_optimize")
    def test_execute(self, mock_optimize, mock_preprocess, mock_post_process, mock_export_data, mock_get_inputs):
        mock_get_inputs.return_value = context
        execute.Executor("", "").execute()

        mock_get_inputs.assert_called()
        mock_preprocess.assert_called()
        mock_optimize.assert_called()
        mock_post_process.assert_called()
        mock_export_data.assert_called()

    @patch.object(execute.PreprocessArcs, "preprocess")
    @patch.object(execute.PreprocessNodes, "preprocess")
    @patch.object(execute.PreprocessOdPairs, "preprocess")
    def test_preprocess(self, mock_od_pairs, mock_nodes, mock_arcs):
        execute.Executor("", "")._preprocess()

        mock_arcs.assert_called()
        mock_nodes.assert_called()
        mock_od_pairs.assert_called()

    @patch.object(execute, "max_demand_pairs")
    @patch.object(execute, "min_cost_pairs")
    @patch.object(execute, "verify_model_output")
    def test_optimize_min_cost(self, mock_verify_output, mock_min_cost, mock_max_demand):
        mock_min_cost.return_value = (10.0, 20.0)
        parameters = Parameters({})
        out_dir = ""
        execute.Executor("", out_dir)._optimize(pd.DataFrame(), pd.DataFrame(), [], parameters, out_dir)

        mock_min_cost.assert_called()
        mock_verify_output.assert_called()
        mock_max_demand.assert_not_called()

    @patch.object(execute, "max_demand_pairs")
    @patch.object(execute, "min_cost_pairs")
    @patch.object(execute, "verify_model_output")
    def test_optimize_max_demand(self, mock_verify_output, mock_min_cost, mock_max_demand):
        mock_max_demand.return_value = (10.0, 20.0)
        parameters = Parameters({"cost_budget": 100.0})
        out_dir = ""
        execute.Executor("", out_dir)._optimize(pd.DataFrame(), pd.DataFrame(), [], parameters, out_dir)

        mock_min_cost.assert_not_called()
        mock_verify_output.assert_called()
        mock_max_demand.assert_called()
