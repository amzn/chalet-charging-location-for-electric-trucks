# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Input parameters."""
from dataclasses import dataclass

from chalet.model.base_json_file import BaseJsonFile


@dataclass()
class InputParameters(BaseJsonFile):
    """User-defined parameters of the network."""

    # Maximal allowed deviation factor from the fastest route.
    dev_factor: float = 1.1

    # Minimum allowed deviation (in minutes) from the fastest route.
    min_deviation: float = 30

    # Budget for additional stations.
    cost_budget: float = float("inf")

    # Truck range with full battery (in km).
    truck_range: float = 300

    # Range withheld from truck_range as safety margin (in km).
    safety_margin: float = 50

    # Maximum charger power output in kW.
    charger_power: float = 360

    # Battery capacity in kWh.
    battery_capacity: float = 540

    # Maximum charging break for each individual recharging stop (in minutes).
    max_fuel_time: float = 45

    # Optimality tolerance for MIP algorithm.
    tolerance: float = 0.0

    # Maximum running time for optimization algorithm (in seconds).
    max_run_time: int = 3600

    # Number of parallel processes for subgraph creation.
    num_proc: int = 1

    # Flag for logging to file.
    log_to_file: bool = True

    @staticmethod
    def get_file_name() -> str:
        """Return file name."""
        return "parameters"
