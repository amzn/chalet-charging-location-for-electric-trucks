# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Post process module after model optimization."""
from typing import Dict, List

import pandas as pd

from chalet.algo.util import calc_station_stats
from chalet.model.input.node_type import NodeType
from chalet.model.parameters import Parameters
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs


class PostProcess:
    """Process data post model optimizations for exporting."""

    def __init__(
        self,
        nodes: pd.DataFrame,
        od_pairs: pd.DataFrame,
        sub_graphs: List,
        parameters: Parameters,
        od_coverage: pd.DataFrame,
        missing: pd.DataFrame,
        export_context: Dict[str, pd.DataFrame],
    ):
        """Initialize data."""
        self.nodes: pd.DataFrame = nodes
        self.od_pairs: pd.DataFrame = od_pairs
        self.sub_graphs: List = sub_graphs
        self.export_context: Dict = export_context
        self.parameters: Parameters = parameters
        self.od_coverage: pd.DataFrame = od_coverage
        self.unknown_sites: pd.DataFrame = missing
        self.od_coverage_file: str = "od_coverage.csv"
        self.stations_file: str = "stations.csv"
        self.missing_file: str = "unknown_sites.csv"

    def postprocess(self):
        """Process od, stations and missing sites data for output files."""
        # Update OD coverage data
        self._process_od_data()
        self.export_context[self.od_coverage_file] = self.od_coverage

        # Update stations data
        is_station = (self.nodes[Nodes.type] == NodeType.STATION).values
        sol_nodes = self.nodes.loc[
            self.nodes[Nodes.real] & is_station,
            [Nodes.id, Nodes.type, Nodes.demand],
        ]
        self.export_context[self.stations_file] = sol_nodes

        # Update missing data
        self.export_context[self.missing_file] = self.unknown_sites

    def _process_od_data(self):
        """Process od pairs and od coverage by adding stations and fuel stops information."""
        calc_station_stats(
            self.nodes,
            self.sub_graphs,
            self.od_pairs,
            self.parameters.battery_capacity,
            self.parameters.dest_range,
            self.parameters.truck_range,
        )
        self.od_coverage = self.od_pairs.loc[
            :,
            (
                OdPairs.origin_id,
                OdPairs.destination_id,
                OdPairs.demand,
                OdPairs.distance,
                OdPairs.feasible,
                OdPairs.stations,
                OdPairs.fuel_stops,
            ),
        ]
        self.od_coverage.rename(columns={OdPairs.distance: OdPairs.direct_distance}, inplace=True)
