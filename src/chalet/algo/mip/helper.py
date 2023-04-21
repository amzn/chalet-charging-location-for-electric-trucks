# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Helper methods for mip algorithms."""
import logging
from typing import List

import networkx as nx
import pandas as pd
import xpress as xp

import chalet.algo.csp as csp
import chalet.algo.util as util
from chalet.common.constants import EPS
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs

logger = logging.getLogger(__name__)


def get_subgraph_indices_and_candidates(od_pairs: pd.DataFrame, nodes: pd.DataFrame, subgraphs: List[nx.DiGraph]):
    """Get candidate nodes, subgraph indices and covered demand from od pairs."""
    is_infeasible = ~od_pairs[OdPairs.feasible]
    is_required = od_pairs[OdPairs.demand] > EPS
    util.check_pair_coverage(nodes, subgraphs, od_pairs)
    covered_demand = od_pairs.loc[od_pairs[OdPairs.covered], OdPairs.demand].sum()
    is_covered = od_pairs[OdPairs.covered]

    subgraph_indices = [
        k for k in range(len(subgraphs)) if is_required[k] and not is_infeasible[k] and not is_covered[k]
    ]

    candidates = nodes.loc[nodes[Nodes.cost] > EPS]
    return candidates, subgraph_indices, covered_demand


def initialize_separator_constraints(model, nodes, subgraphs, od_pairs, subgraph_indices, station_vars, pair_vars=None):
    """Add an initial set of OD separator inequalities to the model."""
    for index in subgraph_indices:
        orig, dest = (
            od_pairs.at[index, OdPairs.origin_id],
            od_pairs.at[index, OdPairs.destination_id],
        )
        sub_graph = subgraphs[index]

        # forward direction
        _add_separator(
            sub_graph,
            nx.reverse_view(sub_graph),
            orig,
            dest,
            nodes,
            pair_vars,
            station_vars,
            model,
            index,
        )

        # backward direction
        _add_separator(
            nx.reverse_view(sub_graph),
            sub_graph,
            dest,
            orig,
            nodes,
            pair_vars,
            station_vars,
            model,
            index,
        )


def _add_separator(
    subgraph: nx.DiGraph,
    reverse_subgraph: nx.DiGraph,
    source,
    out,
    nodes,
    pair_vars,
    station_vars,
    model,
    index,
):
    separator_set = set()
    default_sum = 1.0

    def node_filter(node):
        return node in separator_set or util.is_real(node, nodes)

    while True:
        out_component = set(nx.dfs_preorder_nodes(nx.subgraph_view(subgraph, filter_node=node_filter), source=source))
        if out in out_component:
            break
        boundary = nx.node_boundary(subgraph, out_component)

        def boundary_filter(node):
            return node not in boundary

        away_component = nx.dfs_preorder_nodes(
            nx.subgraph_view(reverse_subgraph, filter_node=boundary_filter), source=out
        )
        separator = nx.node_boundary(reverse_subgraph, away_component)
        if any([not is_candidate(node, nodes) for node in separator]):
            raise RuntimeError("Found non-candidate node in separator")
        if pair_vars is None:
            constr = xp.Sum([station_vars[i] for i in separator]) >= default_sum
        else:
            constr = xp.Sum([station_vars[i] for i in separator]) >= pair_vars[index]
        model.addConstraint(constr)
        separator_set.update(separator)


def get_path_attributes(od_pairs, index, subgraphs, nodes, sol_set):
    orig, dest = od_pairs.at[index, OdPairs.origin_id], od_pairs.at[index, OdPairs.destination_id]
    max_time, max_road_time = (
        od_pairs.at[index, OdPairs.max_time],
        od_pairs.at[index, OdPairs.max_road_time],
    )
    sub_graph = subgraphs[index]

    nx.set_node_attributes(sub_graph, dict(zip(sol_set, [0] * len(sol_set))), Nodes.cost)
    path, path_cost = csp.time_feasible_cheapest_path(sub_graph, orig, dest, max_road_time, max_time)
    nx.set_node_attributes(sub_graph, dict(zip(sol_set, nodes.loc[list(sol_set), Nodes.cost])), Nodes.cost)
    return path, path_cost


def is_candidate(node, nodes):
    return not util.is_real(node, nodes)


def set_model_controls(model, max_run_time, tol):
    """Set control attributes of mip model."""
    model.setControl("maxtime", max_run_time)
    model.setControl("miprelstop", tol)
    model.setControl("presolve", 0)
    model.setControl("lplogstyle", 0)
    model.setControl("lplog", 1000)
    model.setControl("heursearchrootcutfreq", 0)
    model.setControl("heurbeforelp", 0)
    model.setControl("mipthreads", 1)


def verify_model_output(nodes, subgraphs, od_pairs, covered_demand, total_cost):
    """Check the output cost and demand."""
    covered_demand, total_cost = util.check_solution(nodes, subgraphs, od_pairs, covered_demand, total_cost)
    pairs_covered = od_pairs[OdPairs.covered].sum()
    logger.info(f"Covered OD pairs: {pairs_covered} ({round(100 * pairs_covered / len(od_pairs), 2)} %)")
    logger.info(f"Total station cost: {round(total_cost, 2)}")

    inf_demand = od_pairs.loc[~od_pairs[OdPairs.feasible], OdPairs.demand].sum()
    total_demand = od_pairs[OdPairs.demand].sum()
    norm_covered_demand = covered_demand / total_demand
    norm_inf_demand = inf_demand / total_demand
    logger.info(
        f"Final solution: covered demand = {round(covered_demand, 2)} ({round(100 * norm_covered_demand, 2)} %), "
        f"cost = {round(total_cost, 2)}"
    )
    logger.info(f"Time-infeasible demand = {round(inf_demand, 2)} ({round(100 * norm_inf_demand, 2)} %)")
