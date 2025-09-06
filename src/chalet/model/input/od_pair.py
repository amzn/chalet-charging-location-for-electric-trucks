# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Origin Destination Pair in a network."""
from pandera.pandas import Column, DataFrameSchema

from chalet.model.base_csv_file import BaseCsvFile


class OdPair(BaseCsvFile):
    """Schema definition for OD Pair."""

    # ID of the starting point (a site node) of a network route
    origin_id = "ORIGIN_ID"

    # ID of the terminal point (a site node) of a network route
    destination_id = "DESTINATION_ID"

    # Demand value associated with the OD pair
    demand = "DEMAND"

    @staticmethod
    def get_file_name() -> str:
        """Return file name."""
        return "od_pairs"

    @staticmethod
    def get_schema() -> DataFrameSchema:
        """Return dataframe schema."""
        return DataFrameSchema(
            {
                OdPair.origin_id: Column(int, coerce=True),
                OdPair.destination_id: Column(int, coerce=True),
                OdPair.demand: Column(float, required=False, nullable=True, coerce=True),
            }
        )
