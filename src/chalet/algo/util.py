# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Utility methods for mip max demand and min cost models."""
import logging
import random
import time
from typing import List

import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.flow import shortest_augmenting_path

import chalet.algo.csp as csp
from chalet.algo.csp import arc_road_time as road_time_func
from chalet.algo.csp import arc_time as time_func
from chalet.common.constants import CAPACITY, EPS, EPS_INT, MIP_BEST_OBJ_VAL, MIP_OBJ_VAL
from chalet.model.input.node_type import NodeType
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs

logger = logging.getLogger(__name__)

PRIMAL_HEURISTIC_PERIOD = 29  # spacing between primal heuristic calls
ROOT_FRAC_SEP_ROUNDS = PRIMAL_HEURISTIC_PERIOD + 1  # number of fractional separation rounds at root node


class BranchAndBoundInfo:
    """Keeps track of information from branch and bound algorithm"""

    inequality_count: int = 0  # number of inequalities added during callback
    frac_sep_rounds: dict = {}  # number of performed fractional separation rounds per branch-and-bound node
    separation_time: float = 0.0  # time spent in separation callbacks
    heuristic_time: float = 0.0  # time spent in primal heuristic
    checked_subgraphs: dict = {}  # keeps track of subgraphs that were checked in last separation round per node

    def __init__(self, subgraph_indices):
        self.checked_subgraphs[0] = subgraph_indices


def remove_redundancy(solution, nodes, subgraphs, od_pairs, ignore=None):
    """Reduces the given solution container of candidate stations to a minimal subset that covers the same OD pairs.

    All OD pairs that are (infeasible/have zero demand/are flagged as 'ignore') are ignored.
    :param solution: Candidate station nodes that are in the solution (iterable).
    :param nodes: Nodes of the network
    :param subgraphs: Required columns: ORIG_ID, DEST_ID, MAX_TIME, MAX_ROAD_TIME, FEASIBLE, DEMAND
    :param od_pairs: Origin destination pairs
    :param ignore: Optional list with Boolean flag for each OD pair (True if OD pair should be ignored).
    :return: Non redundant candidate stations
    """
    if ignore is None:
        ignore = [False] * len(od_pairs)
    solution_dict = dict(zip(solution, [True] * len(solution)))
    subgraph_indices = [
        k
        for k in range(len(subgraphs))
        if od_pairs.at[k, OdPairs.feasible] and od_pairs.at[k, OdPairs.demand] > 0 and not ignore[k]
    ]

    def is_active(n):
        return solution_dict.get(n)

    def is_candidate_node(n):
        return nodes.at[n, Nodes.cost] > 0

    # determine initial paths
    def is_real_filter(u):
        return is_dummy(u) or not is_candidate_node(u) or is_active(u)

    paths = np.empty(len(subgraphs), dtype=object)
    for k in subgraph_indices:
        path = get_feasible_path(subgraphs[k], k, od_pairs, is_real_filter)
        if not path:
            continue
        paths[k] = path

    # check if node removal changes coverage
    return _update_substitute_paths(
        nodes,
        subgraph_indices,
        subgraphs,
        od_pairs,
        paths,
        is_real_filter,
        is_active,
        solution_dict,
    )


def _update_substitute_paths(
    nodes, subgraph_indices, subgraphs, od_pairs, paths, is_real_filter, is_active, solution_dict
):
    candidate_indices = nodes[nodes[Nodes.cost] > 0].index
    for node in [n for n in candidate_indices if is_active(n)]:
        substitute_paths = []  # path replacements if node is removed
        remove = True

        def filter_func(u):
            return u != node and is_real_filter(u)

        for k in subgraph_indices:
            if paths[k] is None or node not in paths[k]:
                continue

            path = get_feasible_path(subgraphs[k], k, od_pairs, filter_func)
            if not path:
                remove = False
                break
            substitute_paths.append((k, path))

        if remove:
            solution_dict[node] = False
            for k, path in substitute_paths:
                paths[k] = path

    solution = [u for u in candidate_indices if solution_dict.get(u)]
    return solution


def check_pair_coverage(nodes, subgraphs, od_pairs):
    """Check for each OD pair and subgraph specified by existing nodes if a time-feasible route exists.

    Add coverage flags in column "COVERED" of od_pairs.
    """
    num_pairs = len(od_pairs)
    od_pairs[OdPairs.covered] = False

    def is_candidate(n):
        return nodes.at[n, Nodes.cost] > EPS

    def filter_func(u):
        return is_dummy(u) or nodes.at[u, Nodes.real] or not is_candidate(u)

    for k in range(num_pairs):
        path = get_feasible_path(subgraphs[k], k, od_pairs, filter_func)
        if not path:
            continue

        od_pairs.at[k, OdPairs.covered] = True


def remove_redundant_stations(nodes, subgraphs, od_pairs):
    """Remove redundant stations from final solution marked in nodes DataFrame."""
    start = time.time()
    logger.info("Removing redundant stations.")

    is_candidate_node = nodes[Nodes.cost] > EPS
    solution = nodes.loc[is_candidate_node & nodes[Nodes.real]].index

    solution = remove_redundancy(solution, nodes, subgraphs, od_pairs)

    nodes.loc[is_candidate_node, Nodes.real] = False
    nodes.loc[solution, Nodes.real] = True
    total_cost = nodes.loc[nodes[Nodes.real], Nodes.cost].sum()

    end = time.time()
    logger.info(f"Finished in {round(end - start, 2)} secs.")

    return total_cost


def separate_lazy_constraints(
    problem,
    model,
    od_pairs,
    nodes,
    station_vars,
    candidates,
    subgraph_indices,
    subgraphs,
    bb_info,
    demand_vars=None,
    cost_budget=float("inf"),
):
    """
    Separates inequalities at the current node of the branch and bound tree.
    Returns infeasibility status of the node. We never return True, since
    this functions adds any violated inequalities to the model.
    """
    start_time = time.time()
    candidate_arcs = [(u, -u) for u in candidates.index]
    frac_vars = problem.getAttrib("mipinfeas")  # number of fractional variables
    current_node = problem.getAttrib("currentnode")
    parent_node = problem.getAttrib("parentnode")

    x: List = []
    problem.getlpsol(x, None, None, None)
    cut_count = 0

    candidate_vals = [x[model.getIndex(station_vars[u])] for u in candidates.index]
    arc_capacities = dict(zip(candidate_arcs, candidate_vals))

    y = np.array(x)

    if bb_info.frac_sep_rounds.get(current_node) is None:  # initialize fractional separation counter
        bb_info.frac_sep_rounds[current_node] = 0
    if frac_vars > 0:
        if (
            bb_info.frac_sep_rounds.get(current_node) >= 1 and current_node > 1
        ):  # single round of fractional separation per branch-and-bound node
            return False
        elif bb_info.frac_sep_rounds.get(current_node) >= ROOT_FRAC_SEP_ROUNDS:
            return False
        else:
            bb_info.frac_sep_rounds[current_node] += 1

        # determine subset of subgraphs to check for violated inequalities
        # simple strategy: start from those subgraphs that admitted violated inequalities in previous separation round
        if bb_info.checked_subgraphs.get(current_node) is not None:
            subgraphs_to_check = bb_info.checked_subgraphs[current_node]
        else:
            subgraphs_to_check = bb_info.checked_subgraphs[parent_node]
        if len(subgraphs_to_check) == 0:  # if last round checked none, revert to full iteration
            subgraphs_to_check = subgraph_indices

        # increase subset by randomly sampling 50% additional subgraphs for exploration
        num_remaining_indexes = len(subgraph_indices) - len(subgraphs_to_check)
        if num_remaining_indexes > 0:
            random.seed(current_node + bb_info.frac_sep_rounds[current_node])
            remaining_indexes = [idx for idx in subgraph_indices if idx not in subgraphs_to_check]
            subgraphs_to_check += random.sample(
                remaining_indexes, min(num_remaining_indexes, round(0.5 * len(subgraphs_to_check)))
            )
    else:
        subgraphs_to_check = subgraph_indices

    cut_count, violated_subgraphs = _separation_algorithm(
        frac_vars,
        subgraphs_to_check,
        model,
        x,
        od_pairs,
        subgraphs,
        nodes,
        station_vars,
        cut_count,
        arc_capacities,
        problem,
        y,
        demand_vars=demand_vars,
    )

    # full separation round if subset did not give any violated inequalities
    if cut_count == 0 and len(subgraphs_to_check) < len(subgraph_indices):
        cut_count, violated_subgraphs = _separation_algorithm(
            frac_vars,
            subgraph_indices,
            model,
            x,
            od_pairs,
            subgraphs,
            nodes,
            station_vars,
            cut_count,
            arc_capacities,
            problem,
            y,
            demand_vars=demand_vars,
        )

    end_time = time.time()
    sep_time = end_time - start_time
    bb_info.checked_subgraphs[current_node] = violated_subgraphs
    bb_info.inequality_count += cut_count

    heur_time = 0.0
    if cut_count > 0 and (current_node + bb_info.frac_sep_rounds[current_node] - 1) % PRIMAL_HEURISTIC_PERIOD == 1:
        start_time = time.time()
        _primal_heuristic(
            subgraph_indices,
            model,
            od_pairs,
            subgraphs,
            nodes,
            station_vars,
            y,
            current_node,
            demand_vars=demand_vars,
            cost_budget=cost_budget,
        )
        _set_integer_solution(
            problem,
            od_pairs,
            subgraph_indices,
            model,
            station_vars,
            candidates,
            nodes,
            y,
            subgraphs,
            demand_vars=demand_vars,
        )
        end_time = time.time()
        heur_time = end_time - start_time

    bb_info.separation_time += sep_time
    bb_info.heuristic_time += heur_time
    return False


def _primal_heuristic(
    subgraph_indices,
    model,
    od_pairs,
    subgraphs,
    nodes,
    station_vars,
    y,
    current_node,
    demand_vars=None,
    cost_budget=float("inf"),
):
    is_max_demand = demand_vars is not None

    if is_max_demand:
        covered_demands = [y[model.getIndex(demand_vars[k])] * od_pairs.at[k, OdPairs.demand] for k in subgraph_indices]
        # sort OD pairs based on (partially) satisfied demand
        subgraph_indices = [
            k for k, _ in sorted(zip(subgraph_indices, covered_demands), key=lambda pair: pair[1], reverse=True)
        ]

    total_cost = 0.0
    station_sol_dict = dict(zip(station_vars.keys(), [0] * len(station_vars)))
    for k in subgraph_indices:
        sub_graph = subgraphs[k]
        orig, dest = od_pairs.at[k, OdPairs.origin_id], od_pairs.at[k, OdPairs.destination_id]
        max_time, max_road_time = (
            od_pairs.at[k, OdPairs.max_time],
            od_pairs.at[k, OdPairs.max_road_time],
        )

        candidate_nodes = [u for u in sub_graph if is_candidate(u, nodes)]
        reduced_costs = [
            nodes.at[u, Nodes.cost] * max(0.0, 1.0 - y[model.getIndex(station_vars[u])]) for u in candidate_nodes
        ]
        nx.set_node_attributes(sub_graph, dict(zip(candidate_nodes, reduced_costs)), Nodes.cost)
        path, _ = csp.time_feasible_cheapest_path(sub_graph, orig, dest, max_road_time, max_time)
        nx.set_node_attributes(
            sub_graph,
            dict(zip(candidate_nodes, nodes.loc[candidate_nodes, Nodes.cost])),
            Nodes.cost,
        )

        # compute marginal path cost
        path_cost = 0.0
        new_stations = []
        for u in path:
            if is_candidate(u, nodes) and not station_sol_dict[u]:
                station_sol_dict[u] = 1
                path_cost += nodes.at[u, Nodes.cost]
                new_stations.append(u)

        # check path feasibility and save solution
        if path and total_cost + path_cost <= cost_budget:
            total_cost += path_cost
            for u in new_stations:
                y[model.getIndex(station_vars[u])] = 1
            if is_max_demand:
                y[model.getIndex(demand_vars[k])] = 1
        elif is_max_demand:
            y[model.getIndex(demand_vars[k])] = 0

    # set all station variable values
    for key, val in station_sol_dict.items():
        y[model.getIndex(station_vars[key])] = val


def _separation_algorithm(
    frac_vars,
    subgraph_indices,
    model,
    x,
    od_pairs,
    subgraphs,
    nodes,
    station_vars,
    cut_count,
    arc_capacities,
    problem,
    y,
    demand_vars=None,
):
    is_max_demand = demand_vars is not None
    min_demand = 0.5 if frac_vars == 0 else EPS_INT

    def is_active(node):
        return is_real(node, nodes) or x[model.getIndex(station_vars[node])] >= 1.0 - EPS_INT

    def is_int(node):
        return is_active(node) or x[model.getIndex(station_vars[node])] <= EPS_INT

    violated_subgraphs = []
    prev_cut_count = 0
    for k in subgraph_indices:
        if is_max_demand and x[model.getIndex(demand_vars[k])] < min_demand:  # skip if demand is inactive
            continue
        sub_graph = subgraphs[k]
        orig, dest = od_pairs.at[k, OdPairs.origin_id], od_pairs.at[k, OdPairs.destination_id]
        max_time, max_road_time = (
            od_pairs.at[k, OdPairs.max_time],
            od_pairs.at[k, OdPairs.max_road_time],
        )

        path, path_time = csp.shortest_path(nx.subgraph_view(sub_graph, filter_node=is_active), orig, dest, time_func)

        if (frac_vars > 0 and all([is_int(u) for u in sub_graph.nodes])) or frac_vars == 0:
            # integer separation
            if not path:  # only perform separation based on connectivity
                cut_count += _integer_separation(
                    sub_graph,
                    orig,
                    dest,
                    is_active,
                    k,
                    nodes,
                    station_vars,
                    problem,
                    demand_vars,
                )
            else:
                # additionally compute fastest road-time path
                path, path_road_time = csp.shortest_path(
                    nx.subgraph_view(sub_graph, filter_node=is_active),
                    orig,
                    dest,
                    road_time_func,
                )
                if path_time > max_time or path_road_time > max_road_time:
                    cut_count += _integer_time_separation(
                        sub_graph,
                        orig,
                        dest,
                        max_time,
                        max_road_time,
                        is_active,
                        k,
                        nodes,
                        station_vars,
                        problem,
                        demand_vars,
                    )
        elif frac_vars > 0:
            # fractional separation (pure connectivity only)
            if not path:
                cut_count += _fractional_separation(
                    sub_graph,
                    orig,
                    dest,
                    arc_capacities,
                    model,
                    k,
                    x,
                    station_vars,
                    problem,
                    nodes,
                    demand_vars,
                )

        # save subgraph index if cuts were added
        if cut_count > prev_cut_count:
            prev_cut_count = cut_count
            violated_subgraphs.append(k)

    return cut_count, violated_subgraphs


def _integer_separation(sub_graph, orig, dest, is_active, index, nodes, station_vars, problem, demand_vars=None):
    # separator closest to origin
    orig_separator = _get_integer_separator(sub_graph, nx.reverse_view(sub_graph), orig, dest, is_active)
    _add_inequality(orig_separator, index, nodes, station_vars, problem, demand_vars)

    # separator closest to destination
    dest_separator = _get_integer_separator(nx.reverse_view(sub_graph), sub_graph, dest, orig, is_active)
    if dest_separator != orig_separator:
        _add_inequality(dest_separator, index, nodes, station_vars, problem, demand_vars)
        return 2
    else:
        return 1


def _get_integer_separator(sub_graph, reverse_graph, source, out_source, is_active):
    out_component = nx.dfs_preorder_nodes(nx.subgraph_view(sub_graph, filter_node=is_active), source=source)
    boundary = nx.node_boundary(sub_graph, out_component)

    def boundary_filter(node):
        return node not in boundary

    away_component = nx.dfs_preorder_nodes(
        nx.subgraph_view(reverse_graph, filter_node=boundary_filter), source=out_source
    )
    return nx.node_boundary(reverse_graph, away_component)


def _add_inequality(node_set, demand_idx, nodes, station_vars, problem, demand_vars=None):
    if any([is_real(n, nodes) for n in node_set]):
        raise RuntimeError("Some node in the cut is not a candidate station")
    if not node_set:
        raise RuntimeError("Trying to add an inequality for an empty node cut")
    cut_type, row_type = [0], ["G"]
    rhs = [1.0]
    start = [0, len(node_set)]
    colind = [station_vars[n] for n in node_set]
    cut_coef = [1.0] * len(node_set)
    if demand_vars:
        rhs = [0]
        start = [0, len(node_set) + 1]
        colind.append(demand_vars[demand_idx])
        cut_coef.append(-1.0)
    problem.addcuts(cut_type, row_type, rhs, start, colind, cut_coef)


def _integer_time_separation(
    sub_graph,
    orig,
    dest,
    max_time,
    max_road_time,
    is_active,
    index,
    nodes,
    station_vars,
    problem,
    demand_vars=None,
):
    """
    Adds inequalities for time-separators in an integer-valued solution that is not time-feasible
    """
    # separator closest to origin
    best_time_to_dest = nx.single_source_dijkstra_path_length(nx.reverse_view(sub_graph), dest, weight=time_func)

    def tail_is_active(tail, head):
        """Filter function for edges expects two arguments"""
        return is_active(tail)

    time_from_orig = nx.single_source_dijkstra_path_length(
        nx.subgraph_view(sub_graph, filter_edge=tail_is_active), orig, weight=time_func
    )
    best_road_time_to_dest = nx.single_source_dijkstra_path_length(
        nx.reverse_view(sub_graph), dest, weight=road_time_func
    )
    road_time_from_orig = nx.single_source_dijkstra_path_length(
        nx.subgraph_view(sub_graph, filter_edge=tail_is_active), orig, weight=road_time_func
    )

    orig_separator = _get_time_separator(
        time_from_orig,
        road_time_from_orig,
        best_time_to_dest,
        best_road_time_to_dest,
        max_time,
        max_road_time,
        is_active,
        sub_graph,
        orig,
    )
    _add_inequality(orig_separator, index, nodes, station_vars, problem, demand_vars)

    # separator closest to destination
    best_time_from_orig = nx.single_source_dijkstra_path_length(sub_graph, orig, weight=time_func)
    time_to_dest = nx.single_source_dijkstra_path_length(
        nx.subgraph_view(nx.reverse_view(sub_graph), filter_edge=tail_is_active),
        dest,
        weight=time_func,
    )
    best_road_time_from_orig = nx.single_source_dijkstra_path_length(sub_graph, orig, weight=road_time_func)
    road_time_to_dest = nx.single_source_dijkstra_path_length(
        nx.subgraph_view(nx.reverse_view(sub_graph), filter_edge=tail_is_active),
        dest,
        weight=road_time_func,
    )

    dest_separator = _get_time_separator(
        time_to_dest,
        road_time_to_dest,
        best_time_from_orig,
        best_road_time_from_orig,
        max_time,
        max_road_time,
        is_active,
        nx.reverse_view(sub_graph),
        dest,
    )
    if dest_separator != orig_separator:
        _add_inequality(dest_separator, index, nodes, station_vars, problem, demand_vars)
        return 2
    else:
        return 1


def _get_time_separator(
    source_time,
    source_road_time,
    best_dest_time,
    best_dest_road_time,
    max_time,
    max_road_time,
    is_active,
    sub_graph,
    source,
):
    def time_filter(u):
        if (
            source_time.get(u) is None
            or source_road_time.get(u) is None
            or best_dest_time.get(u) is None
            or best_dest_road_time.get(u) is None
        ):
            return False
        else:
            return (
                best_dest_time[u] + source_time[u] <= max_time
                and best_dest_road_time[u] + source_road_time[u] <= max_road_time
            )

    def filter_func(node):
        return is_active(node) and time_filter(node)

    component = nx.dfs_preorder_nodes(nx.subgraph_view(sub_graph, filter_node=filter_func), source=source)
    boundary = nx.node_boundary(sub_graph, component)
    separator = [node for node in boundary if time_filter(node)]
    return separator


def _fractional_separation(
    sub_graph,
    orig,
    dest,
    arc_capacities,
    model,
    index,
    x,
    station_vars,
    problem,
    nodes,
    demand_vars=None,
):
    nx.set_edge_attributes(sub_graph, arc_capacities, CAPACITY)
    try:
        min_cut_val, partition = nx.minimum_cut(sub_graph, orig, dest, capacity=CAPACITY)
    except Exception:
        logger.warning("Default max flow solver crashed. Will try shortest augmenting path.")
        min_cut_val, partition = nx.minimum_cut(
            sub_graph, orig, dest, capacity=CAPACITY, flow_func=shortest_augmenting_path
        )

    dest_component = partition[1] if dest in partition[1] else partition[0]
    min_separator = set(nx.node_boundary(nx.reverse_view(sub_graph), dest_component))

    if demand_vars is not None:
        min_cut_threshold = x[model.getIndex(demand_vars[index])]
    else:
        min_cut_threshold = 1.0 - EPS

    if min_cut_val < min_cut_threshold:
        _add_inequality(min_separator, index, nodes, station_vars, problem, demand_vars)
        return 1
    else:
        return 0


def _set_integer_solution(
    problem, od_pairs, subgraph_indices, model, station_vars, candidates, nodes, y, subgraphs, demand_vars=None
):
    y[y < 1.0 - EPS_INT] = 0  # remove fractional entries
    if demand_vars is not None:
        best_obj = max(problem.getAttrib(MIP_OBJ_VAL), problem.getAttrib(MIP_BEST_OBJ_VAL)) + EPS
        obj = np.sum([y[model.getIndex(demand_vars[k])] * od_pairs.at[k, OdPairs.demand] for k in subgraph_indices])
        if obj > best_obj:
            problem.addmipsol(y)
    else:
        obj = np.sum([y[model.getIndex(station_vars[i])] * nodes.at[i, Nodes.cost] for i in candidates.index])
        best_obj = min(problem.getAttrib(MIP_OBJ_VAL), problem.getAttrib(MIP_BEST_OBJ_VAL)) - EPS
        if obj < best_obj:
            solution = [u for u in candidates.index if y[model.getIndex(station_vars[u])] >= 1.0 - EPS_INT]
            solution = remove_redundancy(solution, nodes, subgraphs, od_pairs)
            y = np.zeros(len(y))
            solution_index = [model.getIndex(station_vars[u]) for u in solution]
            y[solution_index] = 1
            problem.addmipsol(y)


def get_feasible_path(sub_graph, index, od_pairs, filter_func):
    """Get a time feasible path based on road time and max road time bounds."""
    orig, dest = od_pairs.at[index, OdPairs.origin_id], od_pairs.at[index, OdPairs.destination_id]
    max_time, max_road_time = (
        od_pairs.at[index, OdPairs.max_time],
        od_pairs.at[index, OdPairs.max_road_time],
    )
    path = csp.time_feasible_path(
        nx.subgraph_view(sub_graph, filter_node=filter_func), orig, dest, max_road_time, max_time
    )
    return path


def is_dummy(node):
    """Check if node is a dummy node."""
    return node < 0


def is_real(node, nodes):
    """Check if node is real or not."""
    return is_dummy(node) or nodes.at[node, Nodes.cost] < EPS


def is_candidate(node, nodes):
    """Check if node is a candidate station or not."""
    return not is_real(node, nodes)


def check_solution(nodes, subgraphs, od_pairs, claimed_demand, claimed_cost):
    """Check output cost and demand."""
    logger.info("Performing solution check..")

    sol_cost = nodes.loc[nodes[Nodes.real], Nodes.cost].sum()
    is_cost_above_upper_bound = sol_cost > claimed_cost + EPS
    if is_cost_above_upper_bound or sol_cost < claimed_cost < EPS:
        logger.warning(
            f"Solution cost {'higher' if is_cost_above_upper_bound else 'lower'} than expected (claimed / actual):"
            f" {round(claimed_cost, 2)} / {round(sol_cost, 2)}"
        )

    check_pair_coverage(nodes, subgraphs, od_pairs)
    sol_demand = od_pairs.loc[od_pairs[OdPairs.covered], OdPairs.demand].sum()

    is_below_lower_bound = sol_demand < claimed_demand - EPS
    if is_below_lower_bound or sol_demand > claimed_demand + EPS:
        logger.warning(
            f"Covered demand {'lower' if is_below_lower_bound else 'higher'} than expected (claimed / actual):"
            f" {round(claimed_demand, 2)} / {round(sol_demand, 2)}"
        )

    return sol_demand, sol_cost


def calc_station_stats(
    nodes: pd.DataFrame,
    subgraphs: List[nx.Graph],
    od_pairs: pd.DataFrame,
    battery_capacity: float,
    terminal_range: float,
    truck_range: float,
):
    """Attributes to each station data about its usage in terms of demand.
    Attaches for each OD pair the list and number of visited stations.

    :return:
    """
    nodes[Nodes.energy] = 0.0
    kwh_per_km = battery_capacity / truck_range
    nodes[Nodes.demand] = 0.0
    num_pairs = len(od_pairs)

    def is_candidate(u):
        return nodes.at[u, Nodes.cost] > EPS

    def is_real_node(u):
        return (u < 0) or nodes.at[u, Nodes.real]  # negation is remaining candidate (not dummy and not real)

    def filter_func(u):
        return is_real_node(u) or not is_candidate(u)

    od_pairs[OdPairs.stations] = ""
    od_pairs[OdPairs.fuel_stops] = 0
    od_pairs[OdPairs.route_distance] = float("inf")
    od_pairs[OdPairs.route_time] = float("inf")
    for k in range(num_pairs):
        demand = od_pairs.at[k, OdPairs.demand]
        path = get_feasible_path(subgraphs[k], k, od_pairs, filter_func)
        if not path:
            continue

        station_list = []
        # initialize distance and time tracker
        first_node, second_node = path[0], path[1]
        first_arc_attrs = subgraphs[k].edges[first_node, second_node]
        route_dist = first_arc_attrs[Arcs.distance]
        route_time = first_arc_attrs[Arcs.time] + first_arc_attrs[Arcs.fuel_time] + first_arc_attrs[Arcs.break_time]

        for n in range(1, len(path) - 1):  # only consider station nodes
            node = path[n]
            if node < 0:  # ignore dummy nodes
                continue

            station_list.append(node)

            # OD pair data
            nodes.at[node, Nodes.demand] += demand

            if path[n + 1] < 0:  # if station has a dummy node
                out_node, next_node = path[n + 1], path[n + 2]
            else:
                out_node, next_node = node, path[n + 1]
            # charged energy
            arc_attrs = subgraphs[k].edges[out_node, next_node]
            dist = arc_attrs[Arcs.distance]
            nodes.at[node, Nodes.energy] += dist * kwh_per_km * demand
            if nodes.at[next_node, Nodes.type] == NodeType.SITE:
                nodes.at[node, Nodes.energy] += terminal_range * kwh_per_km * demand

            # update time and distance tracker
            route_dist += dist
            route_time += arc_attrs[Arcs.time] + arc_attrs[Arcs.fuel_time] + arc_attrs[Arcs.break_time]

        od_pairs.at[k, OdPairs.stations] = "/".join(str(station) for station in station_list)
        od_pairs.at[k, OdPairs.fuel_stops] = len(station_list)
        od_pairs.at[k, OdPairs.route_distance] = route_dist
        od_pairs.at[k, OdPairs.route_time] = route_time

    nodes[Nodes.energy] = np.around(nodes[Nodes.energy], decimals=1)
    nodes[Nodes.demand] = np.around(nodes[Nodes.demand], decimals=2)
