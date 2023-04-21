# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Methods for creating directed graph using networkx library."""
import gc
import logging
import multiprocessing
import time
from functools import partial
from typing import List

import networkx as nx
import numpy as np
import pandas as pd

from chalet.algo.csp import arc_road_time, arc_time
from chalet.common.constants import ROUND_OFF_FACTOR
from chalet.model.hash_map import Hashmap
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.node_type import NodeType
from chalet.model.input.od_pair import OdPair
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs

logger = logging.getLogger(__name__)


def create_subgraphs(
    od_pairs: pd.DataFrame,
    arcs: pd.DataFrame,
    nodes: pd.DataFrame,
    time_dist_map: Hashmap,
    truck_range: float,
    fuel_time_bound: float,
    num_proc: int,
) -> List[nx.DiGraph]:
    """Create a subgraph for each OD pair based on the arc list of the global graph."""
    num_pairs = len(od_pairs)

    start = time.time()
    logger.info(f"Creating subgraphs for {num_pairs} OD pairs with {num_proc} processes.")

    create_subgraph_ = partial(
        _create_subgraph,
        od_pairs=od_pairs,
        arcs=arcs,
        nodes=nodes,
        time_dist_map=time_dist_map,
        truck_range=truck_range,
        fuel_time_bound=fuel_time_bound,
    )

    with multiprocessing.Pool(processes=num_proc) as pool:
        subgraphs = pool.map(create_subgraph_, od_pairs.index)

    end = time.time()
    logger.info(f"Finished subgraph creation in {round(end-start, ROUND_OFF_FACTOR)} secs.")

    return subgraphs


def _filter_arcs_based_on_transit_time_lower_bounds(
    time_dist_map: Hashmap,
    sub_arcs: pd.DataFrame,
    orig: int,
    dest: int,
    truck_range: float,
    fuel_time_bound: float,
    max_time: float,
    max_road_time: float,
) -> pd.DataFrame:
    """Filters arcs based on transit time lower bound."""
    time_dist_from_orig = time_dist_map[
        np.array(
            [np.ones(len(sub_arcs)) * orig, sub_arcs[Arc.tail_id]],
            dtype=sub_arcs[Arc.tail_id].values.dtype,
        ).transpose()
    ]
    time_dist_to_dest = time_dist_map[
        np.array(
            [sub_arcs[Arc.head_id], np.ones(len(sub_arcs)) * dest],
            dtype=sub_arcs[Arc.head_id].values.dtype,
        ).transpose()
    ]

    # arc road time + other road time
    road_time = time_dist_from_orig[:, 0] + sub_arcs[Arcs.time] + time_dist_to_dest[:, 0]
    distance = time_dist_from_orig[:, 1] + sub_arcs[Arcs.distance] + time_dist_to_dest[:, 1]
    # road time bound + arc break time + fuel time bound
    total_time = road_time + sub_arcs[Arcs.break_time] + distance * (fuel_time_bound / truck_range)

    sub_arcs = sub_arcs[(total_time <= max_time) & (road_time <= max_road_time)]

    return sub_arcs


def _get_arcs_to_and_from_irrelevant_sites(nodes: pd.DataFrame, arcs: pd.DataFrame, orig: int, dest: int):
    """Gets all arcs to and from irrelevant sites."""
    remove = (
        (nodes.loc[arcs[Arc.tail_id], Node.type] == NodeType.SITE).values & (arcs[Arc.tail_id] != orig).values
    ) | ((nodes.loc[arcs[Arc.head_id], Node.type] == NodeType.SITE).values & (arcs[Arc.head_id] != dest).values)
    sub_arcs = arcs[~remove]

    return sub_arcs


def _create_subgraph(
    idx: int,
    od_pairs: pd.DataFrame,
    arcs: pd.DataFrame,
    nodes: pd.DataFrame,
    time_dist_map: Hashmap,
    truck_range: float,
    fuel_time_bound: float,
) -> nx.DiGraph:
    """Create a minimal subgraph for the specified OD pair.

    All arcs that are not on a fastest path between origin and destination are removed.
    The time values are assumed to be fastest connections, in particular they satisfy the triangle inequality.
    """
    orig, dest, max_time = (
        od_pairs.at[idx, OdPair.origin_id],
        od_pairs.at[idx, OdPair.destination_id],
        od_pairs.at[idx, OdPairs.max_time],
    )
    max_road_time = od_pairs.at[idx, OdPairs.max_road_time]

    sub_arcs = _get_arcs_to_and_from_irrelevant_sites(nodes, arcs, orig, dest)

    sub_arcs = _filter_arcs_based_on_transit_time_lower_bounds(
        time_dist_map, sub_arcs, orig, dest, truck_range, fuel_time_bound, max_time, max_road_time
    )

    sub_graph = nx.from_pandas_edgelist(
        sub_arcs,
        Arcs.tail_id,
        Arcs.head_id,
        [Arcs.time, Arcs.fuel_time, Arcs.break_time, Arcs.distance],
        create_using=nx.DiGraph,
    )

    if orig not in sub_graph.nodes or dest not in sub_graph.nodes:
        return nx.DiGraph()

    sub_graph = _remove_redundant_nodes_and_edges(sub_graph, orig, dest, max_road_time, max_time)

    # remove isolated nodes (only once, could lead to more isolates in principle)
    isolates = [
        n
        for n in sub_graph.nodes
        if n != orig and n != dest and (not sub_graph.in_edges(n) or not sub_graph.out_edges(n))
    ]
    sub_graph.remove_nodes_from(isolates)

    # set node costs
    nx.set_node_attributes(sub_graph, nodes[Nodes.cost].to_dict(), Nodes.cost)

    sub_graph = _split_candidate_nodes(sub_graph)

    del sub_arcs
    gc.collect()

    return sub_graph


def _remove_redundant_nodes_and_edges(
    sub_graph: nx.DiGraph, orig: int, dest: int, max_road_time: float, max_time: float
) -> nx.DiGraph:
    # filter triangles at origin and destination (valid since ROAD_TIME satisfies triangle inequality)
    redundant_edges = [(u, v) for u, v in sub_graph.in_edges(sub_graph.successors(orig)) if u != orig]
    sub_graph.remove_edges_from(redundant_edges)
    redundant_edges = [(u, v) for u, v in sub_graph.out_edges(sub_graph.predecessors(dest)) if v != dest]
    sub_graph.remove_edges_from(redundant_edges)

    graph_road_time_from_orig = nx.single_source_dijkstra_path_length(sub_graph, orig, weight=arc_road_time)
    graph_road_time_to_dest = nx.single_source_dijkstra_path_length(
        nx.reverse_view(sub_graph), dest, weight=arc_road_time
    )
    graph_time_from_orig = nx.single_source_dijkstra_path_length(sub_graph, orig, weight=arc_time)
    graph_time_to_dest = nx.single_source_dijkstra_path_length(nx.reverse_view(sub_graph), dest, weight=arc_time)

    if graph_road_time_from_orig.get(dest) is None or graph_road_time_from_orig[dest] > max_road_time:
        return nx.DiGraph()

    if graph_time_from_orig.get(dest) is None or graph_time_from_orig[dest] > max_time:
        return nx.DiGraph()

    redundant_edges = []
    for u, v in sub_graph.edges:
        try:
            graph_road_time = (
                graph_road_time_from_orig[u] + graph_road_time_to_dest[v] + arc_road_time(u, v, sub_graph.edges[u, v])
            )
            graph_time = graph_time_from_orig[u] + graph_time_to_dest[v] + arc_time(u, v, sub_graph.edges[u, v])
            if graph_road_time > max_road_time or graph_time > max_time:
                redundant_edges.append((u, v))
        except KeyError:
            redundant_edges.append((u, v))
    sub_graph.remove_edges_from(redundant_edges)

    del redundant_edges

    return sub_graph


def _split_candidate_nodes(digraph: nx.DiGraph) -> nx.DiGraph:
    """Split candidate nodes.

    Split every non-isolated candidate node (positive cost) into two nodes
    (original/auxiliary) attached with the
    incoming/outgoing arcs and adds a new arc from the original to the auxiliary node.
    The auxiliary node index is the inverse of the original node index.
    The cost of the auxiliary node and all attributes of the new arc are set to 0.
    :param digraph: Must be directed and nodes must have "COST" attribute.
    """
    candidate_nodes = [node for node, attr in digraph.nodes(data=True) if attr[Nodes.cost] > 0]
    for node in candidate_nodes:
        if not digraph.in_edges(node) or not digraph.out_edges(node):  # ignore isolates
            continue
        out_node = -node
        digraph.add_nodes_from([(out_node, {Nodes.cost: 0.0})])
        digraph.add_edges_from([(out_node, v, attr) for (u, v, attr) in digraph.out_edges(node, data=True)])
        digraph.remove_edges_from(list(digraph.out_edges(node)))
        digraph.add_edge(node, out_node)
        (u, v, attr) = list(digraph.in_edges(node, data=True))[0]
        for key in attr.keys():
            digraph.edges[node, out_node][key] = 0.0

    return digraph
