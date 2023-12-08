# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Mixed Integer Programming (MIP) model/algorithm to maximize demand."""
import logging
import traceback
from typing import List

import networkx as nx
import numpy as np
import pandas as pd
import xpress as xp

import chalet.algo.mip.helper as helper
import chalet.algo.util as util
from chalet.common.constants import EPS, MIP_BEST_OBJ_VAL, MIP_OBJ_VAL, ROUND_OFF_FACTOR
from chalet.log_config.config import set_mip_log_file
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs

logger = logging.getLogger(__name__)

DEMAND = "demand"
STATION = "station"


def max_demand_pairs(
    nodes: pd.DataFrame,
    subgraphs: List[nx.DiGraph],
    od_pairs: pd.DataFrame,
    cost_budget: float,
    tol: float,
    max_run_time: int,
    log_dir: str,
):
    """Maximize covered demand on OD pairs within the cost budget."""
    candidates, subgraph_indices, covered_demand = helper.get_subgraph_indices_and_candidates(
        od_pairs, nodes, subgraphs
    )

    if not subgraph_indices or candidates.empty:
        return covered_demand, 0

    demand_vars = xp.vars(subgraph_indices, name=DEMAND, vartype=xp.binary)
    station_vars = xp.vars(candidates.index, name=STATION, vartype=xp.binary)
    model = _build_model(
        candidates, nodes, subgraphs, od_pairs, subgraph_indices, cost_budget, demand_vars, station_vars, log_dir
    )

    # fast heuristic for starting solution
    _construct_initial_solution(model, candidates, nodes, od_pairs, subgraph_indices, subgraphs, cost_budget)

    demand_sol, station_sol = _set_model_attributes_and_solve(
        model,
        demand_vars,
        od_pairs,
        nodes,
        station_vars,
        subgraph_indices,
        subgraphs,
        candidates,
        max_run_time,
        tol,
        cost_budget,
    )
    covered_demand += np.sum(od_pairs.loc[subgraph_indices, OdPairs.demand] * np.array(list(demand_sol.values())))

    station_sol_arr = np.array(list(station_sol.items()))
    station_sol_arr = station_sol_arr[station_sol_arr[:, 1] > 0.5]
    nodes.loc[station_sol_arr[:, 0], Nodes.real] = True

    total_cost = nodes.loc[nodes[Nodes.real], Nodes.cost].sum()

    return covered_demand, total_cost


def _build_model(
    candidates, nodes, subgraphs, od_pairs, subgraph_indices, cost_budget, demand_vars, station_vars, log_dir
):
    logger.info("Building MIP model for maximum demand.")
    model = xp.problem()
    set_mip_log_file(model, log_dir)

    model.addVariable(demand_vars)
    model.addVariable(station_vars)

    helper.initialize_separator_constraints(
        model, nodes, subgraphs, od_pairs, subgraph_indices, station_vars, pair_vars=demand_vars
    )

    # initialize budget constraint
    budget_constraint = xp.Sum([station_vars[i] * nodes.at[i, Nodes.cost] for i in candidates.index]) <= cost_budget
    model.addConstraint(budget_constraint)

    # Set model objective to maximize demand
    objective = xp.Sum([demand_vars[i] * od_pairs.at[i, OdPairs.demand] for i in subgraph_indices])
    model.setObjective(objective, sense=xp.maximize)
    return model


def _construct_initial_solution(model, candidates, nodes, od_pairs, subgraph_indices, subgraphs, cost_budget):
    logger.info("Constructing simple initial solution.")
    demand_dict = dict(zip(subgraph_indices, [0] * len(subgraph_indices)))
    station_dict = dict(zip(candidates.index, [0] * len(candidates)))
    sol: List = []
    init_cost = 0
    init_demand = 0
    sorted_index = od_pairs.loc[subgraph_indices].sort_values(OdPairs.demand, ascending=False).index
    for index in sorted_index:
        demand = od_pairs.at[index, OdPairs.demand]
        path, path_cost = helper.get_path_attributes(od_pairs, index, subgraphs, nodes, sol)
        if init_cost + path_cost > cost_budget:
            continue

        new_nodes = [u for u in path if helper.is_candidate(u, nodes) and not station_dict[u]]
        for u in new_nodes:
            station_dict[u] = 1
            sol.append(u)
        init_cost += path_cost
        demand_dict[index] = 1
        init_demand += demand

    logger.info(f"Found initial solution: covered demand = {init_demand}, cost = {init_cost}")
    model.addmipsol(list(demand_dict.values()) + list(station_dict.values()))


def _set_model_attributes_and_solve(
    model,
    demand_vars,
    od_pairs,
    nodes,
    station_vars,
    subgraph_indices,
    subgraphs,
    candidates,
    max_run_time,
    tol,
    cost_budget,
):
    bb_info = util.BranchAndBoundInfo(subgraph_indices)

    def separate_lazy_constraints(problem, data):
        try:
            return util.separate_lazy_constraints(
                problem,
                model,
                od_pairs,
                nodes,
                station_vars,
                candidates,
                subgraph_indices,
                subgraphs,
                bb_info,
                demand_vars=demand_vars,
                cost_budget=cost_budget,
            )
        except Exception:
            logger.error(f"Problem in callback: {traceback.format_exc()}")

    def pre_check_int_sol(problem, data, soltype, cutoff):
        try:
            return _pre_check_int_sol(
                problem,
                soltype,
                cutoff,
                model,
                demand_vars,
                od_pairs,
                nodes,
                station_vars,
                subgraph_indices,
                subgraphs,
            )
        except Exception:
            logger.error(f"Problem in callback: {traceback.format_exc()}")

    def check_int_sol(problem, data):
        try:
            _check_int_sol(problem, model, demand_vars, od_pairs, nodes, station_vars, subgraph_indices, subgraphs)
        except Exception:
            logger.error(f"Problem in callback: {traceback.format_exc()}")

    model.addcbpreintsol(pre_check_int_sol, None)
    model.addcbintsol(check_int_sol, None)
    model.addcboptnode(separate_lazy_constraints, None)

    helper.set_model_controls(model, max_run_time, tol)

    logger.info("Starting MIP solver.")
    model.solve("d")  # solve with dual simplex

    logger.info("MIP solver finished.")
    logger.info(f"Added inequalities during callback: {bb_info.inequality_count}")
    logger.info(
        f"Total time spent in callbacks for separation: {round(bb_info.separation_time, ROUND_OFF_FACTOR)} secs."
    )
    logger.info(
        f"Total time spent in callbacks for primal heuristic: {round(bb_info.heuristic_time, ROUND_OFF_FACTOR)} secs."
    )
    demand_sol = model.getSolution(demand_vars)
    station_sol = model.getSolution(station_vars)

    return demand_sol, station_sol


def _pre_check_int_sol(
    problem,
    soltype,
    cutoff,
    model,
    demand_vars,
    od_pairs,
    nodes,
    station_vars,
    subgraph_indices,
    subgraphs,
):
    """Check feasibility and improvement of the integer solution.

    Additionally, if the projection onto the feasible set is improving, it is added to the solver.
    """
    if soltype == 0:  # Optimal node solutions are handled by OPTNODE callback
        return False, cutoff

    x: List = []
    problem.getlpsol(x, None, None, None)

    obj = np.sum([x[model.getIndex(demand_vars[k])] * od_pairs.at[k, OdPairs.demand] for k in subgraph_indices])
    best_obj = max(problem.getAttrib(MIP_OBJ_VAL), problem.getAttrib(MIP_BEST_OBJ_VAL)) + EPS

    def sol_filter(node):
        return not helper.is_candidate(node, nodes) or x[model.getIndex(station_vars[node])] > 0.5

    infeasible = False

    for k in subgraph_indices:
        if x[model.getIndex(demand_vars[k])] < 0.5:
            continue

        if obj < best_obj:
            return True, None

        path = util.get_path_attributes(subgraphs[k], k, od_pairs, sol_filter)
        demand = od_pairs.at[k, OdPairs.demand]

        if not path:
            infeasible = True
            x[model.getIndex(demand_vars[k])] = 0
            obj -= demand
            continue

    if infeasible:
        problem.addmipsol(x)
        return True, None

    return False, cutoff


def _check_int_sol(problem, model, demand_vars, od_pairs, nodes, station_vars, subgraph_indices, subgraphs):
    """Check maximality of the demand variables in the integer solution (after acceptance).

    If the demand variables are not maximal, then the improved solution is added to the solver.
    """
    x: List = []
    problem.getlpsol(x, None, None, None)

    def is_active(node):
        return not helper.is_candidate(node, nodes) or x[model.getIndex(station_vars[node])] > 0.5

    sub_optimal = False

    for k in subgraph_indices:
        if x[model.getIndex(demand_vars[k])] > 0.5:
            continue

        path = util.get_path_attributes(subgraphs[k], k, od_pairs, is_active)

        if not path:
            continue

        sub_optimal = True
        x[model.getIndex(demand_vars[k])] = 1

    if sub_optimal:
        problem.addmipsol(x)
