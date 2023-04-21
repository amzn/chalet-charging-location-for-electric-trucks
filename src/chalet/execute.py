# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Execute the process of charging location tool."""
import logging
import time
from typing import Dict

import pandas as pd

from chalet.algo.mip.helper import verify_model_output
from chalet.algo.mip.max_demand_pairs import max_demand_pairs
from chalet.algo.mip.min_cost_pairs import min_cost_pairs
from chalet.common.constants import OD_COVERAGE, ROUND_OFF_FACTOR, SUB_GRAPHS, TRANSIT_TIME_KEY, UNKNOWN_SITES
from chalet.data_io.input_handler import get_all_inputs
from chalet.data_io.output_handler import export_data
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters
from chalet.model.transit_time import TransitTime
from chalet.postprocess.post_process_context import PostProcess
from chalet.preprocess.arcs import PreprocessArcs
from chalet.preprocess.nodes import PreprocessNodes
from chalet.preprocess.od_pairs import PreprocessOdPairs

logger = logging.getLogger(__name__)


class Executor:
    """Execution of the tool."""

    def __init__(self, input_path: str, output_path: str):
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.context: Dict[str, pd.DataFrame] = {}
        self.export_context: Dict[str, pd.DataFrame] = {}

    def execute(self):
        """Start execution of process."""
        # Load context
        self.context = get_all_inputs(self.input_path)

        # create transit time from parameters
        parameters: Parameters = self.context[Parameters.get_file_name()]
        transit_time_provider = TransitTime(parameters.max_road_time_once, parameters.legal_break_time)
        self.context[TRANSIT_TIME_KEY] = transit_time_provider

        logger.info(f"Parameters: {parameters}")

        # Start preprocessing of context
        self._preprocess()

        # Start optimization model
        logger.info("Starting optimization model")
        nodes = self.context[Node.get_file_name()]
        od_pairs = self.context[OdPair.get_file_name()]
        sub_graphs = self.context[SUB_GRAPHS]
        self._optimize(nodes, od_pairs, sub_graphs, parameters, self.output_path)

        # Post process and update export context
        post_process = PostProcess(
            nodes,
            od_pairs,
            sub_graphs,
            parameters,
            self.context[OD_COVERAGE],
            self.context[UNKNOWN_SITES],
            self.export_context,
        )
        post_process.postprocess()

        # Write final output to files
        export_data(self.output_path, self.export_context)

    def _preprocess(self):
        # Start preprocessing of context
        preprocess_start = time.time()
        logger.info("Starting preprocessing of data.")

        preprocess_list = [PreprocessArcs(), PreprocessNodes(), PreprocessOdPairs()]
        for process in preprocess_list:
            preprocess_func = getattr(process, "preprocess")
            preprocess_func(self.context)

        preprocess_end = time.time()
        logger.info(
            f"Total time spent on preprocessing: {round(preprocess_end - preprocess_start, ROUND_OFF_FACTOR)} secs"
        )

    @staticmethod
    def _optimize(nodes, od_pairs, sub_graphs, parameters, log_dir):
        algo_start = time.time()

        if parameters.cost_budget < float("inf"):
            covered_demand, total_cost = max_demand_pairs(
                nodes,
                sub_graphs,
                od_pairs,
                parameters.cost_budget,
                parameters.tolerance,
                parameters.max_run_time,
                log_dir,
            )
        else:
            covered_demand, total_cost = min_cost_pairs(
                nodes, sub_graphs, od_pairs, parameters.tolerance, parameters.max_run_time, log_dir
            )

        algo_end = time.time()
        logger.info(f"Total running time of optimization: {round(algo_end - algo_start, ROUND_OFF_FACTOR)} secs.")
        # Verify model output
        verify_model_output(nodes, sub_graphs, od_pairs, covered_demand, total_cost)
