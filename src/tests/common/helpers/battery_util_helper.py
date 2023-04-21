# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from chalet.common.battery_util import (
    charge_time,
    get_left_range_level_time,
    get_mid_range_level_time,
    get_right_range_level_time,
)

LEFT = 0.2
RIGHT = 0.8
MAX_POWER = 1  # kWh
CAPACITY = 10  # kW
SCALE = 1000
EPSILON = 1 / SCALE
HOURS_TO_MINUTES = 60
REF_FACTOR = CAPACITY / MAX_POWER * HOURS_TO_MINUTES
LEVEL = np.linspace(0, 1, SCALE)
GREEN = "green"
RED = "red"
WHITE = "white"


def check_continuity() -> List[float]:
    first_left_limit = charge_time(LEFT, MAX_POWER, CAPACITY, left=LEFT)
    first_right_limit = charge_time(LEFT + 1e-9, MAX_POWER, CAPACITY, left=LEFT)
    second_left_limit = charge_time(RIGHT, MAX_POWER, CAPACITY, right=RIGHT)
    second_right_limit = charge_time(RIGHT + 1e-9, MAX_POWER, CAPACITY, right=RIGHT)

    if (
        not abs(first_right_limit - first_left_limit) < EPSILON
        and not abs(second_right_limit - second_left_limit) < EPSILON
    ):
        return [LEFT, RIGHT]
    elif not abs(first_right_limit - first_left_limit) < EPSILON:
        return [LEFT, -1]
    elif not abs(second_right_limit - second_left_limit) < EPSILON:
        return [-1, RIGHT]
    return [-1, -1]


def get_invalid_charging_speed() -> Tuple[np.ndarray, np.ndarray]:
    result = _get_battery_charging_function()
    charging_speed = REF_FACTOR
    x = LEVEL[np.roll(result, 1) > result - charging_speed / SCALE]
    y = result[np.roll(result, 1) > result - charging_speed / SCALE]
    return x[1:], y[1:]


def _get_battery_charging_function() -> np.ndarray:
    max_time = REF_FACTOR * (2 * LEFT + (RIGHT - LEFT) + 2 * (1 - RIGHT))
    battery_charging_function = np.piecewise(
        LEVEL,
        [LEVEL < LEFT, np.logical_and(LEFT <= LEVEL, RIGHT >= LEVEL), LEVEL > RIGHT],
        [
            get_left_range_level_time(REF_FACTOR, LEFT),
            get_mid_range_level_time(REF_FACTOR, LEFT),
            get_right_range_level_time(REF_FACTOR, RIGHT, max_time),
        ],
    )
    return battery_charging_function


def make_graph_for_battery_level_time():
    battery_charging_function = _get_battery_charging_function()

    invalid_x, invalid_y = get_invalid_charging_speed()

    original = battery_charging_function.copy()

    plt.xlabel("Charging percentage")
    plt.ylabel("Charging time [minutes]")

    discontinuous_points = check_continuity()

    if battery_charging_function[0] != 0:
        discontinuous_points.append(0.0)

    plot_list = []
    for point in discontinuous_points:
        if point == -1:
            continue
        first, second = int(SCALE * (point - 1 / SCALE)), int(SCALE * (point + 1 / SCALE))
        battery_charging_function[first:second] = None
        key = LEVEL[first:second]
        value = original[first:second]
        if point == 0:
            plot_list.append((np.array([point]), np.array([battery_charging_function[0]])))
        else:
            plot_list.append((key, value))

    plt.plot(LEVEL, battery_charging_function, "g", color=GREEN, label="valid")
    if len(invalid_x) > 1:
        plt.plot(invalid_x, invalid_y, "g", color=RED, label="charging speed to fast")
    for x, y in plot_list:
        if plot_list[0][0][0] == x[0]:
            plt.plot(
                x[0],
                y[0],
                marker="o",
                markersize=5,
                markeredgecolor=RED,
                markerfacecolor=WHITE,
                label="discontinuity",
            )
        else:
            plt.plot(x[0], y[0], marker="o", markersize=5, markeredgecolor=RED, markerfacecolor=WHITE)
        if x[0] != 0 and x[0] != 1:
            plt.plot(x[1], y[1], marker="o", markersize=5, markeredgecolor=RED, markerfacecolor=WHITE)

    plt.legend(loc="upper left")
    plt.show()
