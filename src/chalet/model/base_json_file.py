# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base json file."""
from abc import abstractmethod

from chalet.model.base_file import BaseFile


class BaseJsonFile(BaseFile):
    """Base class for json files."""

    @staticmethod
    @abstractmethod
    def get_file_name() -> str:
        """Return file name."""
        pass
