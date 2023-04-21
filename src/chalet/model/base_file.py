# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base file structure."""
from abc import ABC, ABCMeta, abstractmethod


class BaseFile(ABC, metaclass=ABCMeta):
    """Base class for other files."""

    @staticmethod
    @abstractmethod
    def get_file_name() -> str:
        """Return file name."""
