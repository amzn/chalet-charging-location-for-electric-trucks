# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test model."""
import unittest

from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair


class TestModel(unittest.TestCase):
    """Test model definitions."""

    def test_arcs(self):
        """Test arc definition."""
        assert Arc.get_file_name() == "arcs"

    def test_nodes(self):
        """Test node definition."""
        assert Node.get_file_name() == "nodes"

    def test_od_pairs(self):
        """Test od pair definition."""
        assert OdPair.get_file_name() == "od_pairs"

    def test_something(self):
        abc = "hello"
        self.assertEqual(abc, "hello")
