# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest.mock import patch

import pytest

from chalet.common.battery_util import charge_time, recharge_time
from tests.common.helpers.battery_util_helper import (
    LEFT,
    RIGHT,
    check_continuity,
    get_invalid_charging_speed,
    make_graph_for_battery_level_time,
)

MAX_POWER = 1  # kWh
CAPACITY = 10  # kW
UNUSED = 0


def get_path_module(module) -> str:
    return module.__module__ + "." + module.__name__


class TestChargeTime(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = None

    def test_invalid_level_value_throws_value_error(self):
        with pytest.raises(ValueError):
            charge_time(0.0 - 1e-9, UNUSED, UNUSED)
            charge_time(1.0 + 1e-9, UNUSED, UNUSED)

    def test_low_level_value(self):
        actual = int(charge_time(0.4, MAX_POWER, CAPACITY, LEFT, RIGHT))

        assert actual == 360

    def test_medium_level_value(self):
        actual = int(charge_time(0.1, MAX_POWER, CAPACITY))

        assert actual == 60

    def test_high_level_value(self):
        actual = int(charge_time(1, MAX_POWER, CAPACITY))

        assert actual == 720

    def test_starting_level_of_function(self):
        actual_lower_bound = charge_time(0, MAX_POWER, CAPACITY)

        assert actual_lower_bound == 0, make_graph_for_battery_level_time()

    def test_function_continuity(self):
        left_continuous, right_continuous = check_continuity()

        assert left_continuous == -1 and right_continuous == -1, make_graph_for_battery_level_time()

    def test_if_function_has_valid_charging_speed(self):
        result_x, _ = get_invalid_charging_speed()

        assert len(result_x) < 2, make_graph_for_battery_level_time()


class TestRechargeTime:
    def test_recharge_time_valid(self):
        with patch(get_path_module(charge_time), side_effect=[3, 1]):
            actual = recharge_time(UNUSED, UNUSED, UNUSED, UNUSED)

        assert actual == 2
