# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data class for mip test module."""
import networkx as nx
import pandas as pd
import xpress as xp

from chalet.model.input.node_type import NodeType
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


class MipData:
    """Test dataset for mip test cases."""

    demand_sol = {0: 1}
    station_sol = {0: 0}

    demand_vars = xp.vars([0], name="demand", vartype=xp.binary)
    station_vars = xp.vars([0, 1], name="station", vartype=xp.binary)

    candidates = pd.DataFrame(
        data={
            Nodes.id: [0, 1],
            Nodes.type: [NodeType.STATION, NodeType.STATION],
            Nodes.cost: [1.0, 1.0],
        }
    )

    nodes = pd.DataFrame(data={Nodes.id: [0, 1, 2], Nodes.cost: [1, 2, 3], Nodes.real: [False, False, False]})

    od_pairs = pd.DataFrame(
        data={
            OdPairs.origin_id: [0],
            OdPairs.destination_id: [1],
            OdPairs.demand: [1.0],
            OdPairs.max_time: [5.0],
            OdPairs.max_road_time: [3.0],
        }
    )

    od_pairs_feasible = pd.DataFrame(
        data={
            OdPairs.origin_id: [0, 1],
            OdPairs.destination_id: [1, 2],
            OdPairs.demand: [1.0, 1.0],
            OdPairs.max_time: [5.0, 4.0],
            OdPairs.max_road_time: [3.0, 2.0],
            OdPairs.feasible: [True, True],
            OdPairs.covered: [False, False],
        }
    )

    sub_graph = nx.DiGraph()
    sub_graph.add_node(1, COST=10)
    sub_graph.add_node(2, COST=10)
    sub_graph.add_node(3, COST=10)
    sub_graph.add_edge(1, 2)
    sub_graph.add_edge(2, 3)
    sub_graphs = [sub_graph]
