# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Preprocess od pairs."""
import logging

import pandas as pd

from chalet.common.battery_util import recharge_time
from chalet.common.constants import OD_COVERAGE, SUB_GRAPHS, TIME_DISTANCE_MAP, TRANSIT_TIME_KEY
from chalet.model.hash_map import Hashmap
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters
from chalet.model.transit_time import TransitTime
from chalet.preprocess.od_pairs_helpers import (
    add_direct_distances,
    add_direct_transit_time_od_pairs,
    extract_and_remove_unknown_sites,
    generate_subgraphs_for_od_pairs,
    remove_od_with_same_orig_dest,
    update_missing_od_demand,
)
from chalet.preprocess.preprocess import PreprocessData

logger = logging.getLogger(__name__)


class PreprocessOdPairs(PreprocessData):
    """Pre-processing of od pairs."""

    def preprocess(self, data: dict):
        """Update default demands, remove unknown sites, preprocess and create sub graphs for each pair."""
        od_pairs: pd.DataFrame = data[OdPair.get_file_name()]
        logger.info(f"Processing: {len(od_pairs)} od pairs.")

        update_missing_od_demand(od_pairs)

        extract_and_remove_unknown_sites(od_pairs, data)

        # start preprocessing of od pairs
        od_pairs = self._preprocess_od_pairs(
            od_pairs,
            data[TIME_DISTANCE_MAP],
            data[TRANSIT_TIME_KEY],
            data[Parameters.get_file_name()],
        )
        data[OdPair.get_file_name()] = od_pairs
        data[OD_COVERAGE] = od_pairs

        # create od pair graphs and update the data
        data[SUB_GRAPHS] = self._create_od_pair_graphs(
            data[Parameters.get_file_name()],
            od_pairs,
            data[Arc.get_file_name()],
            data[Node.get_file_name()],
            data[TIME_DISTANCE_MAP],
        )

    @staticmethod
    def _preprocess_od_pairs(
        od_coverage: pd.DataFrame,
        time_dist_map: Hashmap,
        transit_time_provider: TransitTime,
        params: Parameters,
    ) -> pd.DataFrame:
        """Perform preprocessing routines on OD pairs.

        - Remove OD pairs with unknown origin/destination
        - Remove trivial OD pairs (origin = destination)
        - Add node IDs, direct distances and transit time bounds
        """
        add_direct_distances(time_dist_map, od_coverage)

        od_coverage = remove_od_with_same_orig_dest(od_coverage)

        add_direct_transit_time_od_pairs(od_coverage, time_dist_map, params, transit_time_provider)

        return od_coverage

    def _create_od_pair_graphs(
        self,
        params: Parameters,
        od_pairs: pd.DataFrame,
        arcs: pd.DataFrame,
        nodes: pd.DataFrame,
        time_dist_map: Hashmap,
    ) -> list:
        # determine lower bound on full fuel time
        fuel_time_bound = recharge_time(params.min_state, 1, params.charger_power, params.battery_capacity, right=1)

        subgraphs = generate_subgraphs_for_od_pairs(
            params, od_pairs, arcs, nodes, time_dist_map, fuel_time_bound, params.num_proc
        )

        return subgraphs
