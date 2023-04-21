# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Parameters for the model."""
from chalet.exception.data_error import NegativeValueError, ValueOutOfThresholdError
from chalet.model.input.input_parameters import InputParameters


class Parameters(InputParameters):
    """Additional parameters defined based on input parameters."""

    def __init__(self, params: dict):
        """Initialize parameters."""
        super().__init__(**params)

        self.safe_range = self.truck_range - self.safety_margin
        self.min_state = self.safety_margin / self.truck_range

        # break times for single driver according to
        # https://transport.ec.europa.eu/transport-modes/road/social-provisions/driving-time-and-rest-periods_en
        self.max_road_time_once = 270
        self.legal_break_time = 45

        self.min_fuel_time = 0
        self.min_deviation = max(self.min_deviation, 0)

        self.dest_range = 0.5 * self.safe_range
        self.orig_range = 0.5 * self.safe_range

        # Check parameter values
        self.check_params()

    def __repr__(self):
        """Define dictionary-like representation for parameters."""
        return str(self.__dict__)

    def check_params(self):
        """Check parameter range and values."""
        if self.max_fuel_time < 0:
            raise NegativeValueError("Refueling stop time limit must be non negative")
        if self.dev_factor <= 0:
            raise ValueOutOfThresholdError("Transit time deviation factor must be greater than or equal to 1.")
        if self.tolerance < 0:
            raise NegativeValueError("Tolerance should not be negative")
        if self.dest_range > self.safe_range:
            raise ValueOutOfThresholdError("Range at destinations must not exceed maximum effective truck range")
