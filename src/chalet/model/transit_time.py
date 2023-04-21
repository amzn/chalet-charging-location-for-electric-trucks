# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Transit time."""
import numpy as np


class TransitTime:
    """Provide functions for transit time calculations such as adding break time to road time and inverse functions."""

    def __init__(self, max_road_time_once: float, single_break_time: float):
        """Initialize transit times."""
        self.max_road_time_once = max_road_time_once  # maximum continuous road time
        self.single_break_time = single_break_time

    def break_time(self, road_times: float) -> float:
        """Calculate the required break time for given road time."""
        # Break of length single_break_time for every full max_road_time_once
        return np.floor(road_times / self.max_road_time_once) * self.single_break_time

    def full_time(self, road_times: float) -> float:
        """Calculate full transit time for given road time."""
        transit_times = road_times + self.break_time(road_times)
        return transit_times

    def road_time(self, transit_times: float) -> float:
        """Inverse function of full_time (see above)."""
        num_blocks = np.floor(
            transit_times / (self.max_road_time_once + self.single_break_time)
        )  # number of road+break blocks
        frac_time = transit_times - num_blocks * (self.max_road_time_once + self.single_break_time)  # remaining time
        frac_time /= self.max_road_time_once  # remaining time as fraction of max_road_time_once
        temp = np.array([frac_time, np.ones(np.shape(frac_time))])
        road_times = (num_blocks + np.min(temp, axis=0)) * self.max_road_time_once
        return road_times
