# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Arc between two nodes in a network graph."""
from pandera import Check, Column, DataFrameSchema

from chalet.model.base_csv_file import BaseCsvFile


class Arc(BaseCsvFile):
    """Schema definition for Arcs."""

    # ID of the head of arc
    head_id = "HEAD_ID"

    # ID of tail of arc
    tail_id = "TAIL_ID"

    # Transit time (in minutes) for the arc
    time = "TIME"

    # Distance (in km) for the arc
    distance = "DISTANCE"

    @staticmethod
    def get_file_name() -> str:
        """Return file name."""
        return "arcs"

    @staticmethod
    def get_schema() -> DataFrameSchema:
        """Return dataframe schema."""
        return DataFrameSchema(
            {
                Arc.head_id: Column(int, coerce=True),
                Arc.tail_id: Column(int, coerce=True),
                Arc.time: Column(float, Check.ge(0), coerce=True),
                Arc.distance: Column(float, Check.ge(0), coerce=True),
            }
        )
