# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Battery utility."""
import logging

import numpy as np

logger = logging.getLogger(__name__)


HOURS_TO_MINUTES = 60


def get_left_range_level_time(ref_factor: float, left: float):
    return lambda level: ref_factor * (2 * np.sqrt(left)) * np.sqrt(level)


def get_mid_range_level_time(ref_factor: float, left: float):
    return lambda level: ref_factor * (left + level)


def get_right_range_level_time(ref_factor: float, right: float, max_time: float):
    return lambda level: max_time - ref_factor * (2 * np.sqrt(1 - right) * np.sqrt(1 - level))


def charge_time(level: float, max_power: float, capacity: float, left: float = 0.0, right: float = 0.8) -> float:
    """Return the time to charge the battery from 0 to level.

    The model assumes a linear increase in power output from 0 to left, a constant maximal power output
    from left to right and a linear decrease in power output from right to 1.

    :param level: Desired battery level after charging from 0, must be in range [0,1].
    :param max_power: Maximal power output of charger in kW.
    :param capacity: Capacity of the battery in kWh.
    :param left: Left boundary of maximal power output range (in [0,1]).
    :param right: Right boundary of maximal power output range (in [0,1]).
    :return: Time required to charge from 0 to level in minutes.
    """
    if level < 0 or level > 1:
        logger.error(f"Input battery level: {level}")
        raise ValueError("Specified battery level must be in range [0,1].")

    ref_factor = capacity / max_power * HOURS_TO_MINUTES  # reference factor from linear model in minutes
    # Time bound for charging, with half charging speed available on average for left and right ranges.
    max_time = ref_factor * (2 * left + (right - left) + 2 * (1 - right))

    if 0 <= level <= left:
        return get_left_range_level_time(ref_factor, left)(level)
    elif left <= level <= right:
        return get_mid_range_level_time(ref_factor, left)(level)
    else:
        return get_right_range_level_time(ref_factor, right, max_time)(level)


def recharge_time(
    from_level: float,
    to_level: float,
    max_power: float,
    capacity: float,
    left: float = 0.0,
    right: float = 0.8,
) -> float:
    """Return the time to recharge from_level -> to_level, according to the battery model defined in charge_time."""
    return charge_time(to_level, max_power, capacity, left, right) - charge_time(
        from_level, max_power, capacity, left, right
    )
