# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Preprocess nodes."""
import logging

import pandas as pd

from chalet.common.constants import EPS
from chalet.model.input.node import Node
from chalet.model.input.node_type import NodeType
from chalet.model.processed_nodes import Nodes
from chalet.preprocess.preprocess import PreprocessData

logger = logging.getLogger(__name__)


class PreprocessNodes(PreprocessData):
    """Pre-processing of nodes."""

    def preprocess(self, data: dict):
        """Mark active/current nodes in the network."""
        node_key = Node.get_file_name()
        nodes: pd.DataFrame = data[node_key]
        logger.info(f"Processing: {len(nodes)} nodes.")

        is_station = (nodes[Node.type] == NodeType.STATION).values
        is_candidate = (nodes[Node.cost] > EPS).values  # only candidate stations are assumed to have positive cost
        num_sites = len(nodes[nodes[Node.type] == NodeType.SITE])
        num_stations = len(nodes[is_station])
        logger.info(f"Number of sites: {num_sites}. Number of stations: {num_stations}")

        nodes[Nodes.real] = False  # marks the active stations -> output
        nodes.loc[~is_candidate, Nodes.real] = True  # non-candidate stations are active
