# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base csv file."""
from abc import abstractmethod

from pandera import DataFrameSchema

from chalet.model.base_file import BaseFile


class BaseCsvFile(BaseFile):
    """Base class for csv files."""

    @staticmethod
    @abstractmethod
    def get_schema() -> DataFrameSchema:
        """Return schema."""
