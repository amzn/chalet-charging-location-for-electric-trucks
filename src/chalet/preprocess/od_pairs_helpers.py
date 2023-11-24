# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import time
from typing import List

import networkx as nx
import numpy as np
import pandas as pd

from chalet.algo.csp import time_feasible_path
from chalet.algo.graph import create_subgraphs
from chalet.common.constants import ROUND_OFF_FACTOR, UNKNOWN_SITES
from chalet.model.hash_map import Hashmap
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters
from chalet.model.processed_od_pairs import OdPairs
from chalet.model.transit_time import TransitTime

logger = logging.getLogger(__name__)


def add_direct_distances(time_dist_map: Hashmap, od_coverage: pd.DataFrame):
    direct_distances = time_dist_map.get(od_coverage[[OdPair.origin_id, OdPair.destination_id]])[:, 1]
    od_coverage[OdPairs.distance] = direct_distances


def remove_od_with_same_orig_dest(od_coverage: pd.DataFrame):
    num_pairs_all = len(od_coverage)
    od_coverage = od_coverage[od_coverage[OdPair.origin_id] != od_coverage[OdPair.destination_id]]
    od_coverage.reset_index(drop=True, inplace=True)
    if len(od_coverage) < num_pairs_all:
        logger.info(f"Removed trivial OD pairs (origin = destination). OD pairs remaining: {len(od_coverage)}")

    logger.info("Will report OD coverage based on un-aggregated OD pairs.")
    return od_coverage


def aggregate_identical_od_pairs(od_pairs: pd.DataFrame):
    num_pairs_all = len(od_pairs)
    od_pairs.loc[:, OdPairs.legs] = 1  # Number of different legs the OD pair represents
    od_pairs.loc[:, [OdPair.demand]] = od_pairs.groupby([OdPair.origin_id, OdPair.destination_id])[
        [OdPair.demand]
    ].transform("sum")
    od_pairs.drop_duplicates(
        subset=[OdPair.origin_id, OdPair.destination_id],
        inplace=True,
        ignore_index=True,
    )
    if len(od_pairs) < num_pairs_all:
        logger.info(f"Aggregated OD pairs with identical locations. Distinct OD pairs remaining: {len(od_pairs)}")


def add_direct_transit_time_od_pairs(
    od_pairs: pd.DataFrame,
    time_dist_map: Hashmap,
    params: Parameters,
    transit_time_provider: TransitTime,
):
    direct_times = time_dist_map.get(od_pairs[[OdPair.origin_id, OdPair.destination_id]])[:, 0]
    arr = np.array([direct_times, direct_times]).transpose()
    arr[:, 0] += params.min_deviation
    arr[:, 1] *= params.dev_factor
    buffered_direct_times = np.max(arr, axis=1)  # buffered road transit times
    od_pairs.loc[:, OdPairs.max_time] = transit_time_provider.full_time(buffered_direct_times)  # adds all break times
    od_pairs.loc[:, OdPairs.max_road_time] = buffered_direct_times


def check_pair_feasibility(subgraphs: list, od_pairs: pd.DataFrame):
    """Check for each OD pair if the subgraph contains a time-feasible route.

    Add feasibility flag to OD pairs and returns sum of infeasible demands.
    """
    logger.info("Checking time feasibility of OD pairs..")
    start_time = time.perf_counter()
    num_pairs = len(od_pairs)
    if num_pairs != len(subgraphs):
        raise ValueError("Number of sub-graphs and OD pairs mismatch")
    od_pairs[OdPairs.feasible] = False

    for k in range(len(od_pairs)):
        orig, dest = (
            od_pairs.at[k, OdPair.origin_id],
            od_pairs.at[k, OdPair.destination_id],
        )
        max_time, max_road_time = (
            od_pairs.at[k, OdPairs.max_time],
            od_pairs.at[k, OdPairs.max_road_time],
        )

        path = time_feasible_path(subgraphs[k], orig, dest, max_road_time, max_time)

        if path:
            od_pairs.at[k, OdPairs.feasible] = True

    end_time = time.perf_counter()
    logger.info(f"Finished in {round(end_time - start_time, ROUND_OFF_FACTOR)} secs.")


def generate_subgraphs_for_od_pairs(
    params: Parameters,
    od_pairs: pd.DataFrame,
    arcs: pd.DataFrame,
    nodes: pd.DataFrame,
    time_dist_map: Hashmap,
    fuel_time_bound: float,
    num_proc_sub: int,
) -> List[nx.DiGraph]:
    subgraphs = create_subgraphs(
        od_pairs,
        arcs,
        nodes,
        time_dist_map,
        params.safe_range,
        fuel_time_bound,
        num_proc_sub,
    )
    check_pair_feasibility(subgraphs, od_pairs)
    pairs_feasible = od_pairs[OdPairs.feasible].sum()
    logger.info(
        f"Feasible OD pairs: {pairs_feasible} ({round(100 * pairs_feasible / len(od_pairs), ROUND_OFF_FACTOR)} %)"
    )

    inf_demand = od_pairs.loc[~od_pairs[OdPairs.feasible], OdPair.demand].sum()
    total_demand = od_pairs[OdPair.demand].sum()
    logger.info(f"Total demand across OD pairs: {round(total_demand, ROUND_OFF_FACTOR)}")
    logger.info(
        f"Feasible demand: {round(total_demand - inf_demand, ROUND_OFF_FACTOR)} "
        f"({round(100 * (total_demand - inf_demand) / total_demand, ROUND_OFF_FACTOR)} %). "
    )

    return subgraphs


def update_missing_od_demand(od_pairs: pd.DataFrame):
    default_demand = 1.0
    if OdPair.demand not in od_pairs:
        od_pairs[OdPair.demand] = default_demand
    od_pairs[OdPair.demand] = od_pairs[OdPair.demand].fillna(value=default_demand)


def get_unknown_sites(od_pairs: pd.DataFrame, nodes: pd.DataFrame) -> pd.Series:
    """Extract and remove unknown origin or destinations that are not defined in nodes."""
    # check missing ids in nodes
    missing_orig = od_pairs.loc[~od_pairs[OdPair.origin_id].isin(nodes[Node.id]), OdPair.origin_id]
    missing_dest = od_pairs.loc[~od_pairs[OdPair.destination_id].isin(nodes[Node.id]), OdPair.destination_id]
    missing = pd.concat([missing_orig, missing_dest], ignore_index=True)
    missing.drop_duplicates(inplace=True)

    return missing


def extract_and_remove_unknown_sites(od_pairs: pd.DataFrame, data: dict):
    missing = get_unknown_sites(od_pairs, data[Node.get_file_name()])
    num_pairs_all = len(od_pairs)
    od_pairs.drop(
        od_pairs[od_pairs[OdPair.origin_id].isin(missing) | od_pairs[OdPair.destination_id].isin(missing)].index,
        inplace=True,
    )
    od_pairs.reset_index(drop=True, inplace=True)
    if len(od_pairs) < num_pairs_all:
        logger.info(f"Removed OD pairs with unknown origin or destination. OD pairs remaining: {len(od_pairs)}")
    data[UNKNOWN_SITES] = missing
