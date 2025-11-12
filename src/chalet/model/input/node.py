# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Node in a network graph."""
from pandera.pandas import Check, Column, DataFrameSchema

from chalet.model.base_csv_file import BaseCsvFile
from chalet.model.input.node_type import NodeType


class Node(BaseCsvFile):
    """Schema definition for nodes of network graph."""

    # Unique identifier of the node
    id = "ID"

    # Type of the node, e.g. charging station, site etc.
    type = "TYPE"

    # Cost of the station node, 0 for sites
    cost = "COST"

    # Latitude of a station, needed for plotting
    latitude = "LATITUDE"

    # Longitude of a station, needed for plotting
    longitude = "LONGITUDE"

    # Name of the node
    name = "NAME"

    @staticmethod
    def get_file_name() -> str:
        """Return file name."""
        return "nodes"

    @staticmethod
    def get_schema() -> DataFrameSchema:
        """Return dataframe schema."""
        return DataFrameSchema(
            {
                Node.id: Column(int, coerce=True),
                Node.type: Column(str, Check.isin(NodeType), coerce=True),
                Node.cost: Column(float, Check.ge(0), coerce=True),
                Node.latitude: Column(float, required=False, coerce=True),
                Node.longitude: Column(float, required=False, coerce=True),
                Node.name: Column(str, required=False, nullable=True, coerce=True),
            }
        )
