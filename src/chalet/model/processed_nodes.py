# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Processed nodes."""
from chalet.model.input.node import Node


class Nodes:
    """Definition of processed nodes."""

    id = Node.id
    type = Node.type
    cost = Node.cost
    latitude = Node.latitude
    longitude = Node.longitude
    name = Node.name
    real = "REAL"
    energy = "ENERGY"
    demand = "DEMAND"
    distance = "DISTANCE"
