# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""String Enum."""
from enum import Enum


class StrEnum(str, Enum):  # Derive from str to make the enum json-serializable
    """Base class for creating enumerated constants that are also subclasses of str."""

    def __str__(self) -> str:
        """Str representation."""
        return str(self.value)

    def __repr__(self) -> str:
        """Str representation."""
        return str(self)

    @staticmethod
    def _generate_next_value_(name, *_):
        return name
