# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Customised hash-map."""
import numpy as np
from hirola import HashTable


class Hashmap:
    """Bundle hirola HashTable into a more convenient hashmap."""

    def __init__(self, keys, values, key_type, value_type, default_value):
        """Initialize keys and values in the hashmap."""
        self.key_type = key_type
        self.value_type = value_type
        self.length = len(keys)
        self.hash_tab = HashTable(self.length * 1.3, dtype=key_type)  # 30% size overhead for speedup
        self.values = np.empty(self.hash_tab.max + 1, dtype=value_type)
        self.values[self.hash_tab.add(keys)] = values
        self.values[-1] = default_value

    def __reduce__(self):
        """Define this for pickling / un-pickling.

        :return: Function and arguments to be called upon deserialization
        """
        return Hashmap, (
            self.hash_tab.keys,
            self.get(self.hash_tab.keys),
            self.key_type,
            self.value_type,
            self.values[-1],
        )

    def set(self, keys, values):
        """Set key and corresponding value in the map."""
        self.values[self.hash_tab.add(keys)] = values

    def get(self, keys):
        """Get value for given key from the map."""
        return self.values[self.hash_tab.get(keys)]

    def __getitem__(self, keys):
        """Get item from hashmap."""
        return self.values[self.hash_tab.get(keys)]

    def __repr__(self):
        """Define custom representation of the map."""
        return (
            "Keys: \n"
            + self.hash_tab.keys.__repr__()
            + "\nValues (unordered, last is fallback): \n"
            + self.values.__repr__()
        )

    def __str__(self):
        """Define string representation of map."""
        return (
            "Keys: \n"
            + self.hash_tab.keys.__str__()
            + "\nValues (unordered, last is fallback): \n"
            + self.values.__str__()
        )

    def __len__(self):
        """Get length of the map."""
        return self.length
