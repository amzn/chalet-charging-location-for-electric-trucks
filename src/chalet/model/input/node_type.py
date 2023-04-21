# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Type of nodes in a network."""
from enum import auto

from chalet.common.strenum import StrEnum


class NodeType(StrEnum):
    """Enum strings of node types in a network."""

    SITE = auto()
    STATION = auto()
