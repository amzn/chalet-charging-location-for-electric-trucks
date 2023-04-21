# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""CSP or Constrained Shortest Path First algorithm methods.

It finds the shortest path fulfilling a set of constraints. The constraints here are time or road time feasible paths.
These are helper methods for algo and preprocessing modules.
"""
from typing import Callable, Dict, List, Tuple

import networkx as nx

from chalet.common.constants import EPS
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes

INF_VALUE = float("inf")


def time_feasible_path(graph: nx.Graph, orig: int, dest: int, max_road_time: float, max_time: float) -> List[int]:
    """Compute a path in graph from orig to dest that satisfies bounds on road time and road time + fuel time.

    Returns [] if no path within the bounds is found.
    """
    path, path_time = _road_time_bounded_fastest_path(graph, orig, dest, max_road_time)

    if path_time == INF_VALUE:
        return []
    # If path time doesn't satisfy the road time bound, check for total time bound
    if path_time > max_time:
        path, path_road_time = _time_bounded_fastest_road_path(graph, orig, dest, max_time)
        if path_road_time > max_road_time:
            return []

    return path


def _road_time_bounded_fastest_path(graph: nx.Graph, orig: int, dest: int, max_road_time: float) -> Tuple[list, float]:
    """Find path with minimum time that satisfies road time bound."""
    return _larac(graph, orig, dest, max_road_time, arc_road_time, arc_time)


def _time_bounded_fastest_road_path(graph: nx.Graph, orig: int, dest: int, max_time: float) -> Tuple[list, float]:
    """Find path with minimum road time that satisfies total time bound."""
    return _larac(graph, orig, dest, max_time, arc_time, arc_road_time)


def _larac(
    graph: nx.Graph,
    orig: int,
    dest: int,
    bound: float,
    weight_func: Callable[[int, int, Dict[str, float]], float],
    length_func: Callable[[int, int, Dict[str, float]], float],
) -> Tuple[List[int], float]:
    """Heuristic algorithm for the weight bounded shortest path problem.

    It is based on Lagrange relaxation (Lagrange relaxation-based aggregated cost or LARAC).
    The path length is heuristically minimized while maintaining the bound on the path weight.
    [1] Jüttner et al. Lagrange Relaxation Based Method for the QoS Routing Problem. 2001

    :param graph:
    :param orig: Origin node
    :param dest: Destination node
    :param bound: Weight bound
    :param weight_func: Edge weight function (tail, head, attr_dict -> float)
    :param length_func: Edge length function (tail, head, attr_dict -> float)
    :return: path, path_length
    """

    def calc_weight(s_path: List[int]) -> float:
        weight = 0.0
        for index in range(len(s_path) - 1):
            weight += weight_func(s_path[index], s_path[index + 1], graph.edges[s_path[index], s_path[index + 1]])
        return weight

    def calc_length(s_path: List[int]) -> float:
        length = 0.0
        for index in range(len(s_path) - 1):
            length += length_func(s_path[index], s_path[index + 1], graph.edges[s_path[index], s_path[index + 1]])
        return length

    def calc_cost(s_path: List[int], cost_fun) -> float:
        cost = 0
        for index in range(len(s_path) - 1):
            cost += cost_fun(s_path[index], s_path[index + 1], graph.edges[s_path[index], s_path[index + 1]])
        return cost

    def cost_func(tail: int, head: int, attr: Dict[str, float]) -> float:
        return length_func(tail, head, attr) + model * weight_func(tail, head, attr)

    spath, spath_length = shortest_path(graph, orig, dest, length=length_func)

    if spath_length == INF_VALUE:
        return [], INF_VALUE

    if calc_weight(spath) <= bound:
        return spath, spath_length

    wpath, wpath_weight = shortest_path(graph, orig, dest, length=weight_func)

    if wpath_weight > bound:
        return [], INF_VALUE

    while True:
        model = (calc_length(wpath) - calc_length(spath)) / (calc_weight(spath) - calc_weight(wpath))

        path, path_cost = shortest_path(graph, orig, dest, length=cost_func)

        if path_cost == INF_VALUE:  # error handling
            return [], INF_VALUE

        if abs(path_cost - calc_cost(spath, cost_func)) < EPS:
            return wpath, calc_length(wpath)

        if calc_weight(path) <= bound:
            wpath = path
        else:
            spath = path


def shortest_path(graph: nx.Graph, orig: int, dest: int, length) -> Tuple[list, float]:
    """Compute the shortest path in networkx.graph from orig to dest w.r.t. length.

    If no path exists (or either node is not found), then [], inf is returned.
    """
    try:
        path_length, path = nx.bidirectional_dijkstra(graph, orig, dest, weight=length)
    except (nx.NetworkXNoPath, nx.NodeNotFound, ValueError):
        path_length = INF_VALUE
        path = []

    return path, path_length


def arc_time(tail: int, head: int, attr: Dict[str, float]) -> float:
    """Total time including fuel and break time.

    This is also used as weight function in dijkstra path length algorithm which needs 3 positional arguments.
    """
    return attr[Arcs.time] + attr[Arcs.fuel_time] + attr[Arcs.break_time]


def arc_road_time(tail: int, head: int, attr: Dict[str, float]) -> float:
    """Road time of an arc.

    This is also used as weight function in dijkstra path length algorithm which needs 3 positional arguments.
    """
    return attr[Arcs.time]


def time_feasible_cheapest_path(
    graph: nx.DiGraph, orig: int, dest: int, max_road_time: float, max_time: float
) -> Tuple[List[int], float]:
    """Compute the cheapest path in graph from orig to dest.

    It satisfies bounds on road time and road time + fuel time.If no path within the bounds is found,
    then [], inf is returned. We want to minimize cost approximately.
    """
    path, path_cost = _road_time_bounded_cheapest_path(graph, orig, dest, max_road_time)

    if not path:
        return [], INF_VALUE

    path_time = 0.0
    for i in range(0, len(path) - 1):
        path_time += arc_time(path[i], path[i + 1], graph.edges[path[i], path[i + 1]])

    if path_time > max_time:
        path, path_cost = _time_bounded_cheapest_path(graph, orig, dest, max_time)
    else:
        return path, path_cost

    if not path:
        return [], INF_VALUE

    path_road_time = 0.0
    for i in range(0, len(path) - 1):
        path_road_time += arc_road_time(path[i], path[i + 1], graph.edges[path[i], path[i + 1]])

    if path_road_time > max_road_time:
        return [], INF_VALUE
    else:
        return path, path_cost


def _time_bounded_cheapest_path(graph: nx.DiGraph, orig: int, dest: int, max_time: float) -> Tuple[List[int], float]:
    """"""

    def arc_cost(tail: int, head: int, attr: Dict):
        return _arc_cost(graph, head)

    return _larac(graph, orig, dest, max_time, arc_time, arc_cost)


def _road_time_bounded_cheapest_path(
    graph: nx.DiGraph, orig: int, dest: int, max_road_time: float
) -> Tuple[List[int], float]:
    def arc_cost(tail, head, attr):
        return _arc_cost(graph, head)

    return _larac(graph, orig, dest, max_road_time, arc_road_time, arc_cost)


def _arc_cost(graph: nx.DiGraph, head: int) -> float:
    return graph.nodes[head][Nodes.cost]
