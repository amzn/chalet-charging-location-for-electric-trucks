# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Mixed Integer Programming (MIP) model/algorithm to minimize cost."""
import logging
import traceback
from typing import List, Set

import networkx as nx
import numpy as np
import xpress as xp

import chalet.algo.csp as csp
import chalet.algo.mip.helper as helper
import chalet.algo.util as util
from chalet.common.constants import ROUND_OFF_FACTOR
from chalet.log_config.config import set_mip_log_file
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs

logger = logging.getLogger(__name__)

DEMAND = "demand"
STATION = "station"


def min_cost_pairs(nodes, subgraphs, od_pairs, tol, max_run_time, log_dir):
    """Minimize cost of full OD pair demand coverage."""
    candidates, subgraph_indices, covered_demand = helper.get_subgraph_indices_and_candidates(
        od_pairs, nodes, subgraphs
    )

    if candidates.empty:
        return covered_demand, 0

    model = xp.problem()
    station_vars = {}
    for i in candidates.index:
        station_vars[i] = model.addVariable(name=f"{STATION}_{i}", vartype=xp.binary)
    model = _build_model(candidates, nodes, subgraphs, od_pairs, subgraph_indices, station_vars, model, log_dir)

    # fast heuristic for starting solution
    _construct_initial_solution(model, candidates, nodes, od_pairs, subgraph_indices, subgraphs, station_vars)

    station_sol = _set_model_attributes_and_solve(
        model,
        station_vars,
        subgraph_indices,
        od_pairs,
        nodes,
        subgraphs,
        candidates,
        max_run_time,
        tol,
    )

    covered_demand += od_pairs.loc[subgraph_indices, OdPairs.demand].sum()
    station_sol_arr = np.array(list(station_sol.items()))
    station_sol_arr = station_sol_arr[station_sol_arr[:, 1] > 0.5]
    nodes.loc[station_sol_arr[:, 0], Nodes.real] = True

    total_cost = util.remove_redundant_stations(nodes, subgraphs, od_pairs)

    return covered_demand, total_cost


def _build_model(candidates, nodes, subgraphs, od_pairs, subgraph_indices, station_vars, model, log_dir):
    logger.info("Building MIP model to minimize cost.")

    set_mip_log_file(model, log_dir)
    helper.initialize_separator_constraints(
        model, nodes, subgraphs, od_pairs, subgraph_indices, station_vars, pair_vars=None
    )

    # Set model objective to minimize cost
    objective = xp.Sum([station_vars[i] * nodes.at[i, Nodes.cost] for i in candidates.index])
    model.setObjective(objective, sense=xp.minimize)
    return model


def _construct_initial_solution(model, candidates, nodes, od_pairs, subgraph_indices, subgraphs, station_vars):
    logger.info("Running heuristic for initial solution.")
    sol_set: Set = set()
    for k in subgraph_indices:
        path, path_cost = helper.get_cheapest_path(od_pairs, k, subgraphs, nodes, sol_set)
        candidate_nodes = [u for u in path if helper.is_candidate(u, nodes)]
        sol_set.update(candidate_nodes)

    init_sol = util.remove_redundancy(sol_set, nodes, subgraphs, od_pairs)
    n_vars = len(station_vars)
    init_sol_vec = np.zeros(n_vars)
    var_to_pos = {var: idx for idx, var in enumerate(station_vars.values())}

    for node in init_sol:
        var = station_vars[node]
        pos = var_to_pos[var]
        init_sol_vec[pos] = 1
    init_cost = np.sum(
        [init_sol_vec[model.getIndex(station_vars[i])] * nodes.at[i, Nodes.cost] for i in candidates.index]
    )
    logger.info(f"Constructed initial solution. Cost = {init_cost}")
    model.addmipsol(init_sol_vec)


def _pre_check_int_sol(problem, model, station_vars, subgraph_indices, od_pairs, nodes, subgraphs, cutoff):
    x = problem.getCallbackSolution()

    def sol_filter(u):
        return not helper.is_candidate(u, nodes) or x[model.getIndex(station_vars[u])] > 0.5

    for k in subgraph_indices:
        orig, dest = od_pairs.at[k, OdPairs.origin_id], od_pairs.at[k, OdPairs.destination_id]
        max_time, max_road_time = (
            od_pairs.at[k, OdPairs.max_time],
            od_pairs.at[k, OdPairs.max_road_time],
        )

        path = csp.time_feasible_path(
            nx.subgraph_view(subgraphs[k], filter_node=sol_filter),
            orig,
            dest,
            max_road_time,
            max_time,
        )

        if not path:
            return True, None

    return False, cutoff


def _set_model_attributes_and_solve(
    model, station_vars, subgraph_indices, od_pairs, nodes, subgraphs, candidates, max_run_time, tol
):
    bb_info = util.BranchAndBoundInfo(subgraph_indices)

    def separate_lazy_constraints(problem, data):
        try:
            return util.separate_lazy_constraints(
                problem, model, od_pairs, nodes, station_vars, candidates, subgraph_indices, subgraphs, bb_info
            )
        except Exception:
            logger.error(f"Problem in callback: {traceback.format_exc()}")

    def pre_check_int_sol(problem, data, soltype, cutoff):
        try:
            if soltype == 0:  # if solution is found as optimal node relaxation, do not reject
                return False, cutoff
            return _pre_check_int_sol(
                problem, model, station_vars, subgraph_indices, od_pairs, nodes, subgraphs, cutoff
            )
        except Exception:
            logger.error(f"Problem in callback: {traceback.format_exc()}")

    model.addcbpreintsol(pre_check_int_sol, None)  # callback when integer solution is found
    model.addcboptnode(separate_lazy_constraints, None)  # callback for optimal node relaxation

    helper.set_model_controls(model, max_run_time, tol)

    logger.info("Starting MIP solver..")

    model.solve("d")  # solve with dual simplex

    logger.info("MIP solver finished.")
    logger.info(f"Added inequalities during callback: {bb_info.inequality_count}")
    logger.info(
        f"Total time spent in callbacks for separation: {round(bb_info.separation_time, ROUND_OFF_FACTOR)} secs."
    )
    logger.info(
        f"Total time spent in callbacks for primal heuristic: {round(bb_info.heuristic_time, ROUND_OFF_FACTOR)} secs."
    )
    station_sol = model.getSolution(station_vars)
    return station_sol
